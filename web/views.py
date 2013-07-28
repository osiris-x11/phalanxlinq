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
from rest import _db, ENTITIES
from collections import OrderedDict

def search(request):
    def trim_trailing_zeros(code):
        while code[-1] == '0' and len(code)>2:
            code = code[0:-1]
        return code

    MAX_RESULTS = 2000
    q = request.GET.get('q', '')
    opts = request.GET.getlist('opts')
    db = _db()
#    exp = '^' + re.escape(q)
#    rows = _db().Firmographics.find({'Company': {'$regex':exp }}, {'_id':0})

    rows = []
    c = { 'rows' : [] }
    settings = db.settings.find_one({'_id' : 1})

    fil = {
#            'Addl' : {
#                'MinorityIndicator' : 'Y',
#            },
#            'Location.State' : 'TX',
#            'Addl.MinorityIndicator' : 'Y',
#            'Addl.VeteranOwnedIndicator' : 'Y',
    }
    if 'minority' in opts:
        fil['Addl.MinorityIndicator'] = 'Y'
    if 'woman' in opts:
        fil['Addl.WomanOwnedBusinessEnterpriseIndicator'] = 'Y'
    if 'veteran' in opts:
        fil['Addl.VeteranOwnedIndicator'] = 'Y'
    if 'full' not in opts and settings and settings['SICs'] and len(settings['SICs']):
        sics = settings['SICs']
        fil['$or'] = [
            { 'Industry.SICs.Code' : re.compile('^' + trim_trailing_zeros(code)) } for code in sics
        ]

#        rows = _db().Firmographics.find({'Company': re.compile('' + re.escape(q), re.IGNORECASE) }, {'_id':0})
    if len(q):
        rows = db.command("text", "companies", search=q, filter=fil, project={"_id": 0}, limit=MAX_RESULTS)
        c = { 'rows' : [dict(r['obj'].items() + {'_score' : r['score']}.items()) for r in rows['results']] }
    else:
        rows = db.companies.find(fil, limit = MAX_RESULTS).sort('AnnualSalesUSD', -1)
        c = { 'rows' : rows }


#    c['rows_json'] = json.dumps(c['rows'])
    c['next_url'] = reverse('search') + '?'
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
