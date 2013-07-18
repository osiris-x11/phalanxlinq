import logging
from functools import wraps
from django.core.cache import cache
import json
from django.http import HttpResponse, HttpRequest, Http404

logging.basicConfig(level=logging.INFO)

def _json(f):
    response = HttpResponse(content_type='application/json')
    response.content = json.dumps(f) if not isinstance(f, (str, unicode)) else f
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Authorization'
    return response


class AccessDeniedError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def cacheme(cachekeyprefix=None, timeout=None):
    if timeout is None and type(cachekeyprefix) is int:
        timeout = cachekeyprefix
        cachekeyprefix = None
    print cachekeyprefix, timeout

    def decorator(f):
#        if cachekeyprefix is None:
#            cachekeyprefix = f.func_name
        @wraps(f)
        def cacher(*args, **kwargs):
            if cachekeyprefix is None:
                cachekeyprefix = f.func_name
            # The non-keyword parameters used to call the function are used as the keys
            cachekey = cache.make_key(':'.join(map(str,(cachekeyprefix,) + args[1:])))
            if cachekey in cache:
                logging.info('Cache hit for key [%s]' % cachekey)
                return cache.get(cachekey)
            else:
                logging.info('Cache miss for key [%s, %s]' % (cachekey, timeout))
                val = f(*args, **kwargs)
                cache.set(cachekey, val, timeout=timeout)
                return val
        return cacher
    return decorator


def cacheme(cachekeyprefix, timeout=None):
    def decorator(f):
        @wraps(f)
        def cacher(*args, **kwargs):
#            key = json.dumps({'prefix' : cachekeyprefix, 'args' : args[1:], 'kwargs': ['%s:%s' % (k, kwargs.get(k)) for k in sorted(kwargs.keys())] })
            std_args = args[1:] if len(args) and isinstance(args[0], HttpRequest) else args
            params = [cachekeyprefix] + list(std_args) + ['%s:%s' % (k, kwargs.get(k)) for k in sorted(kwargs.keys())]
            print params
#            print key
#            params += 
#            print 'args', len(args), kwargs
            # The non-keyword parameters used to call the function are used as the keys
            cachekey = cache.make_key(':'.join(map(str,params)))
            if cachekey in cache:
                logging.info('Cache hit for key [%s]' % cachekey)
                return cache.get(cachekey)
            else:
                logging.info('Cache miss for key [%s, %s]' % (cachekey, timeout))
                val = f(*args, **kwargs)
                cache.set(cachekey, val, timeout=timeout)
                return val
        return cacher
    return decorator

def rest_json():
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            request = args[0]
            if request.method == 'OPTIONS':
                return _json({})
            try:
                val = f(*args, **kwargs)
                return _json(val)
            except Http404:
                raise
            except Exception as e:
                response = _json({'error': { 'message' : '%s' % e } })
                response.status = 403
                return response


        return wrapper
    return decorator

def auth():
    def decorator(f):
        @wraps(f)
        def auther(*args, **kwargs):
            request = args[0]
            token = request.META.get('HTTP_AUTHORIZATION', request.GET.get('authorization'))
            ok = auth_maxcv_token(token)
            if ok:
                val = f(*args, **kwargs)
                return val
            else:
                raise Exception('access denied with token %s' % token)
#                return {'error': { 'message' : 'access denied'} }
        return auther
    return decorator