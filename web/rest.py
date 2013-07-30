from decorators import *
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from loader import _db
import requests
from bs4 import BeautifulSoup
from decimal import *
import json

from pymongo import Connection

@csrf_exempt
@rest_json()
def mongo_q(request, dataset):
    coll = _db()[dataset]
    s = 'TODO'

    return s

def mongo_rest_raw(coll_name, query):
    resp = requests.get('http://localhost:28017/hit/%s?%s' % (coll_name, query))
    return resp.json

@csrf_exempt
@rest_json()
def user_company(request, duns):
    db = _db()
    cos = db.user_companies
    with_details = request.GET.get('with') == 'details'

    def append_detail(co):
        if not with_details:
            return co
        deets = db.companies.find_one({'DUNS' : co['DUNS']})
        return dict(co.items() + deets.items())

    user_id = 1
    spec = { 'user_id' : user_id, 'DUNS' : duns }
    proj = { '_id' : 0 }

    if duns == '' and request.method == 'GET':
        return [append_detail(co) for co in cos.find({ 'user_id': user_id }, proj)]

    co = cos.find_one(spec, proj)

    if request.method=='POST':
        doc = json.loads(request.raw_post_data)
        if co:
            cos.update(spec, { '$set' : doc })
        else:
            doc = dict(spec.items() + doc.items())
#            spec['active'] = True
            cos.insert(doc)
    elif request.method=='GET':
        pass
    return cos.find_one(spec, proj)


@csrf_exempt
@rest_json()
def mongo_rest_proxy(request, dataset):
    qs = request.META.get('QUERY_STRING', '')
    if qs:
        qs = '?' + qs
    url = dataset + qs
#    return url

    resp = requests.get('http://localhost:28017/hit/%s' % url)
    return resp.json
#    hit/Firmographics/?limit=-10

@csrf_exempt
@rest_json()
def proxy(request, dataset):
    qs = request.META.get('QUERY_STRING', '')
    if qs:
        qs = '?' + qs

    return azure_get(dataset + qs)
