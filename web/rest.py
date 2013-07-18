from decorators import *
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging
import requests
from bs4 import BeautifulSoup

AZURE_BASE = 'https://api.datamarket.azure.com/DNB/DeveloperSandbox/v1/'

# http://localhost:8000/rest/dnb/Firmographics?$filter=DUNSNumber%20eq%20%27001005032%27

@cacheme('azure_get', 3600)
def azure_get(dataset):
    url = AZURE_BASE + dataset

    resp = requests.get(url, auth=('', settings.ACCOUNT_KEY))
    soup = BeautifulSoup(resp.text, features='xml')

    def xform_entry(entry):
        props = {prop.name : prop.text for prop in entry.find('properties').find_all()}
        return props

    items = [xform_entry(e) for e in soup.find_all('entry')]

    next_url = None
    for link in soup.find_all('link'):
        if link['rel']=='next':
            next_url = '?' + link['href'].split('?')[1]
    return { 'items' : items, 'next' : next_url }

@csrf_exempt
@rest_json()
def proxy(request, dataset):
    qs = request.META.get('QUERY_STRING', '')
    if qs:
        qs = '?' + qs

    return azure_get(dataset + qs)

    ## here's a way to get all...
    i = 0
    rv = None
    items = []
    while True:
        print i, qs
        rv = azure_get(dataset + qs)
        items += rv['items']
        qs = rv['next']
        if qs is None:
            break
        i += 1

    return items
