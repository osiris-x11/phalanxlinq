from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.views.decorators.cache import cache_page
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
import logging
import re
import json
from loader import _db, ENTITIES
from collections import OrderedDict
from math import ceil
from urllib import quote

def layer_user_prefs(prefs, co):
    pass



def get_user_prefs(db, user_id = 1):
    user_settings = db.settings.find_one({'_id' : user_id})
    user_companies = db.user_companies.find({'user_id' : user_id, 'active' : True})
    return {
        'SICs' : user_settings['SICs'] if user_settings else [],
        'companies' : user_companies,
    }


def search(request):
    def trim_trailing_zeros(code):
        while code[-1] == '0' and len(code)>2:
            code = code[0:-1]
        return code

    MAX_PER_PAGE = 500
#    SEARCH_LIMIT = 1000
    q = request.GET.get('q', '')
    opts = request.GET.getlist('opts')
    page_num = request.GET.get('page', 1)
    try:
        page_num = int(page_num)
    except:
        page_num = 1
    start_offset = (page_num-1) * MAX_PER_PAGE


    db = _db()
    prefs = get_user_prefs(db)

    rows = []
    c = { 'rows' : [], 'totalRows' : 0 }

    proj = {
        '_id' : 0,
        'Addl' : 0,
        'Linkage' : 0,
    }
    fil = {}

    flag_alls = [opt for opt in opts if opt != 'full']
    if len(flag_alls):
        fil['Flags'] = { '$all' : flag_alls }

    if 'full' not in opts and len(prefs['SICs']):
        sics = prefs['SICs']
        fil['$or'] = [
            { 'Industry.SICs.Code' : re.compile('^' + trim_trailing_zeros(code)) } for code in sics
        ]

    if len(q):
        rows = db.command("text", "companies", search=q, filter=fil, project=proj)
        c['totalRows'] = rows['stats']['nfound']
        rows['results'] = rows['results'][start_offset:start_offset+MAX_PER_PAGE]
        c['rows'] = [dict(r['obj'].items() + {'_score' : r['score']}.items()) for r in rows['results']]
    else:
        rows = db.companies.find(fil, proj).sort('AnnualSalesUSD', -1)
        c['totalRows'] = rows.count()
        rows = rows[start_offset:start_offset+MAX_PER_PAGE]
        c['rows'] = [r for r in rows]

    # pagination
    num_pages = int(ceil(float(c['totalRows']) / MAX_PER_PAGE))
    c['pages'] = [ { 'num': n, 'url' : reverse('search') + '?q=' + quote(q) + (''.join(['&opts=' + opt for opt in opts]) ) +'&page=%s' % n }
        for n in range(1, num_pages + 1) ]
    c['page_num'] = page_num
    c['pages_prev'] = [pg for pg in c['pages'] if pg['num'] == page_num - 1] 
    c['pages_next'] = [pg for pg in c['pages'] if pg['num'] == page_num + 1] 

    c['rows_json'] = json.dumps(c['rows'])
    c['q'] = q
    c['opts'] = opts
    return render(request, 'web/search.html', c)

def company(request, duns):
    db = _db()

#    all_info = { entity : db[entity].find_one({'DUNSNumber': duns}, {'_id':0}) for entity in ENTITIES }
    all_info = _db().companies.find_one({'_id' : duns})
    all_info['Addl'] = OrderedDict(sorted(all_info['Addl'].items()))
    all_info = OrderedDict(sorted(all_info.items()))

    c = { 'co_json' : json.dumps(all_info), 'co': all_info }

    return render(request, 'web/company.html', c)


def settings(request):
    db = _db()
    if request.method == 'POST':
        sic = request.POST.getlist('sic')
        db.settings.update({'_id' : 1}, {'SICs' : sic, '_id' : 1}, True)
        print sic
    sics = [r for r in db.sic.find({}, {'_id':0}).sort('code')]
    c = {
        'settings' : db.settings.find_one({'_id' : 1}),
        'sics' : sics
    }
    return render(request, 'web/settings.html', c)
