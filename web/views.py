from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.views.decorators.cache import cache_page
from django.shortcuts import render, redirect, get_object_or_404
import logging
import re
import json
from rest import _db

def search(request):
    q = request.GET.get('q', '')
#    exp = '^' + re.escape(q)
#    rows = _db().Firmographics.find({'Company': {'$regex':exp }}, {'_id':0})

    rows = _db().Firmographics.find({'Company': re.compile('' + re.escape(q), re.IGNORECASE) }, {'_id':0})



    c = { 'rows' : [r for r in rows] }
    c['rows_json'] = json.dumps(c['rows'])

    return render(request, 'web/search.html', c)
