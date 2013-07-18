from decorators import *
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging
import requests
from bs4 import BeautifulSoup

from pymongo import Connection


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

def azure_get_all(dataset):
    i = 0
    qs = ''
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

def _db():
    conn = Connection('localhost')
    db = conn.hit
    return db

def populate_mongo():

    entities = ['LocationLatLong', 'Firmographics', 'FamilyHierarchy', 'Demographics', 'PublicRecords', 'Green',
        'Minority', 'Women', 'Veteran', 'Disadvantaged']

    conn = Connection('localhost')
    db = conn.hit

    for entity in entities:
        coll = db[entity]
        coll.remove()
        items = azure_get_all(entity)
        print 'inserting...'
        coll.insert(items)
        print 'indexing...'
        coll.ensure_index('DUNSNumber')
        print 'done'


@csrf_exempt
@rest_json()
def mongo_q(request, dataset):
    conn = Connection('localhost')
    db = conn.hit
    coll = db[dataset]
    s = 'TODO'

    return s

def mongo_rest_raw(coll_name, query):
    resp = requests.get('http://localhost:28017/hit/%s?%s' % (coll_name, query))
    return resp.json

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
