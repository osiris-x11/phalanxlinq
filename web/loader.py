from decorators import *
from django.conf import settings
import requests
from bs4 import BeautifulSoup
from decimal import *
from pymongo import Connection
from time import sleep

AZURE_BASE = 'https://api.datamarket.azure.com/DNB/DeveloperSandbox/v1/'
ENTITIES = ['LocationLatLong', 'Firmographics', 'FamilyHierarchy', 'Demographics', 'PublicRecords', 'Green',
    'Minority', 'Women', 'Veteran', 'Disadvantaged']

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
    conn = Connection('localhost')
    db = conn.hit

    for entity in ENTITIES:
        coll = db[entity]
        coll.remove()
        items = azure_get_all(entity)
        print 'inserting...'
        coll.insert(items)
        print 'indexing...'
        coll.ensure_index('DUNSNumber')
        print 'done'

def consolidate():
    conn = Connection('localhost')
    db = conn.hit

    master = db.companies

    maps = {
'PublicRecords' : """
  BankruptcyDate
  Bankruptcyindicator
  CongressDistrict
  Debarrment
  NetWorth
  NumberofJudgments
  NumberofLiens
  NumberofSuits
  OutOfBusinessInd
  SuitsLiensJudgmentsIndicator
  """,
'Green' : """
  AlaskanNativeCorporationIndicator
  CongressDistrict
  GreenBusinessIndicator
  GreenCertificationDate1
  GreenCertificationDate2
  GreenCertificationDate3
  GreenCertificationDate4
  GreenCertificationExpirationDate1
  GreenCertificationExpirationDate2
  GreenCertificationExpirationDate3
  GreenCertificationExpirationDate4
  GreenCertificationNumber1
  GreenCertificationNumber2
  GreenCertificationNumber3
  GreenCertificationNumber4
  GreenSourceCodeName1
  GreenSourceCodeName2
  GreenSourceCodeName3
  GreenSourceCodeName4
  GreenSourceLevelCode1
  GreenSourceLevelCode2
  GreenSourceLevelCode3
  GreenSourceLevelCode4""",
'Minority' : """
  AlaskanNativeCorporationIndicator
  CongressDistrict
  HistoricallyBlackCollegeorUniversityMinorityInstitutionIndicator
  Minority1DateReceivedbyDnB
  Minority2DateReceivedbyDnB
  MinorityBusinessEnterpriseIndicator
  MinorityBusinessEnterpriseIndicator1
  MinorityBusinessEnterpriseIndicator2
  MinorityCertificationCode1
  MinorityCertificationCode2
  MinorityCertificationDate1
  MinorityCertificationDate2
  MinorityCertificationExpirationDate1
  MinorityCertificationExpirationDate2
  MinorityCertificationNumber1
  MinorityCertificationNumber2
  MinorityClassificationCode1
  MinorityClassificationCode2
  MinorityIndicator
  MinoritySourceCodeName1
  MinoritySourceCodeName2
  MinoritySourceLevelCode1
  MinoritySourceLevelCode2
  SmallBusinessIndicator
  """,
'Women' : """
  AlaskanNativeCorporationIndicator
  CongressDistrict
  SmallBusinessIndicator
  StateAbbrv
  WomanOwned1DateReceivedbyDnB
  WomanOwned2DateReceivedbyDnB
  WomanOwnedBusinessEnterpriseIndicator
  WomanOwnedBusinessEnterpriseIndicator1
  WomanOwnedBusinessEnterpriseIndicator2
  WomanOwnedCertificationCode1
  WomanOwnedCertificationCode2
  WomanOwnedCertificationDate1
  WomanOwnedCertificationDate2
  WomanOwnedCertificationExpirationDate1
  WomanOwnedCertificationExpirationDate2
  WomanOwnedCertificationNumber1
  WomanOwnedCertificationNumber2
  WomanOwnedIndicator
  WomanOwnedSourceCodeName1
  WomanOwnedSourceCodeName2
  WomanOwnedSourceLevelCode1
  WomanOwnedSourceLevelCode2
  """,
'Veteran' : """
  AlaskanNativeCorporationIndicator
  CongressDistrict
  SmallBusinessIndicator
  DisabledVeteranBusinessEnterpriseIndicator
  DisabledVeteranBusinessEnterpriseIndicator1
  DisabledVeteranBusinessEnterpriseIndicator2
  DisadvantagedVeteranEnterpriseIndicator
  DisadvantagedVeteranEnterpriseIndicator1
  DisadvantagedVeteranEnterpriseIndicator2
  ServiceDisabledVeteranOwnedIndicator
  ServiceDisabledVeteranOwnedIndicator1
  ServiceDisabledVeteranOwnedIndicator2
  Veteran1DateReceivedbyDnB
  Veteran2DateReceivedbyDnB
  VeteranBusinessEnterpriseIndicator
  VeteranBusinessEnterpriseIndicator1
  VeteranBusinessEnterpriseIndicator2
  VeteranCertificationCode1
  VeteranCertificationCode2
  VeteranCertificationDate1
  VeteranCertificationDate2
  VeteranCertificationExpirationDate1
  VeteranCertificationExpirationDate2
  VeteranCertificationNumber1
  VeteranCertificationNumber2
  VeteranOwnedIndicator
  VeteranSourceCodeName1
  VeteranSourceCodeName2
  VeteranSourceLevelCode1
  VeteranSourceLevelCode2
  VietnamVeteranOwnedIndicator
  VietnamVeteranOwnedIndicator1
  VietnamVeteranOwnedIndicator2
  """,
'Disadvantaged' : """
  AlaskanNativeCorporationIndicator
  CertifiedSmallBusinessCertificationDate1
  CertifiedSmallBusinessCertificationDate2
  CertifiedSmallBusinessCertificationExpirationDate1
  CertifiedSmallBusinessCertificationExpirationDate2
  CertifiedSmallBusinessCertificationNumber1
  CertifiedSmallBusinessCertificationNumber2
  CertifiedSmallBusinessIndicator
  CertifiedSmallBusinessSourceCodeName1
  CertifiedSmallBusinessSourceCodeName2
  CertifiedSmallBusinessSourceLevelCode1
  CertifiedSmallBusinessSourceLevelCode2
  DisabledOwned1DateReceivedbyDnB
  DisabledOwned2DateReceivedbyDnB
  DisabledOwnedBusinessIndicator
  DisabledOwnedCertificationCode1
  DisabledOwnedCertificationCode2
  DisabledOwnedCertificationDate1
  DisabledOwnedCertificationDate2
  DisabledOwnedCertificationExpirationDate1
  DisabledOwnedCertificationExpirationDate2
  DisabledOwnedCertificationNumber1
  DisabledOwnedCertificationNumber2
  DisabledOwnedSourceCodeName1
  DisabledOwnedSourceCodeName2
  DisabledOwnedSourceLevelCode1
  DisabledOwnedSourceLevelCode2
  DisadvantagedBusinessEnterprise1DateReceivedbyDnB
  DisadvantagedBusinessEnterprise2DateReceivedbyDnB
  DisadvantagedBusinessEnterpriseCertificationCode1
  DisadvantagedBusinessEnterpriseCertificationCode2
  DisadvantagedBusinessEnterpriseCertificationDate1
  DisadvantagedBusinessEnterpriseCertificationDate2
  DisadvantagedBusinessEnterpriseCertificationExpirationDate1
  DisadvantagedBusinessEnterpriseCertificationExpirationDate2
  DisadvantagedBusinessEnterpriseCertificationNumber1
  DisadvantagedBusinessEnterpriseCertificationNumber2
  DisadvantagedBusinessEnterpriseIndicator
  DisadvantagedBusinessEnterpriseSourceCodeName1
  DisadvantagedBusinessEnterpriseSourceCodeName2
  DisadvantagedBusinessEnterpriseSourceLevelCode1
  DisadvantagedBusinessEnterpriseSourceLevelCode2
  HubZoneCertificationIndicator
  LaborSurplusAreaIndicator
  SmallBusinessIndicator
  SmallDisadvantagedBusinessCertificationCode
  SmallDisadvantagedBusinessDateReceivedbyDnB
  SmallDisadvantagedBusinessEntryDate
  SmallDisadvantagedBusinessExitDate
  SmallDisadvantagedBusinessIndicator
  SmallDisadvantagedBusinessSourceLevelCode
  SmallDisadvantagedBusinessSourceName"""
  }

    maps ={ k: [r.strip() for r in v.strip().split('\n')] for k,v in maps.items() }

    addl_fields = []
    for c, fields in maps.items():
        for field in fields:
            if field not in addl_fields:
                addl_fields.append(field)
#    print addl_fields
#    exit()

    def xform_loc(ft_rec, ty):
        tyo = ty + 'Organization'
        sales = None
        if 'ty' + 'AnnualSalesUSDollars' in ft_rec:
            amt = ft_rec[ty + 'AnnualSalesUSDollars']
            if amt != '':
                sales = int(Decimal(amt))
        if ft_rec[ty + 'DUNS'] == '000000000':
            return None
        return {
            "DUNS" : ft_rec[ty + 'DUNS'],
            'Name' : ft_rec[tyo + 'Name'],
            "Location" : {
                'Street1' : ft_rec[tyo + 'Address'],
                'Street2' : ft_rec[tyo + 'Address2'],
                'City' : ft_rec[tyo + 'City'],
                'State' : ft_rec[tyo + 'StateAbbrv'],
                'PostalCode' : ft_rec[tyo + 'PostalCode'],
                'Country' : ft_rec[tyo + 'Country'],
            },
            'AnnualSalesUSD' :  sales
        }

    def xform(rec):
        prefix = rec['InternationalDialingCode']
        duns = rec['DUNSNumber']

        ft = db.FamilyHierarchy.find_one({'DUNSNumber' : duns})
        geo = db.LocationLatLong.find_one({'DUNSNumber' : duns})
  
        if prefix != '' and prefix != '0':
            prefix = '+' + prefix + ' '
        return {
            '_id' : rec['DUNSNumber'],
            'DUNS' : rec['DUNSNumber'],
            'Name' : rec['Company'],
            'Location' : {
                'Name' : rec['Company'],
                'Street1' : rec['Address'],
                'Street2' : rec['Address2'],
                'City' : rec['City'],
                'State' : rec['StateAbbrv'],
                'PostalCode' : rec['ZipCode'],
                'Country' : rec['Country'],
                'Phone' : (prefix + rec['Phone']) if rec['Phone'] else None,
                'Fax' : (prefix + rec['Fax']) if rec['Fax'] else None,
                'AccuracyCode' : geo['AccuracyCode'] if geo else None,
                'Latitude' : geo['Latitude'] if geo else None,
                'Longitude' : geo['Longitude'] if geo else None,
            },
            'Linkage' : {
                'Parent' : xform_loc(ft, 'Parent'),
                'HQ' : xform_loc(ft, 'HQ'),
                'DomesticUltimate' : xform_loc(ft, 'DomesticUltimate'),
                'GlobalUltimate' : xform_loc(ft, 'GlobalUltimate'),
            },
            'DBAs' : [rec['DoingBusinessAs%s'%n] for n in range(1,6) if rec['DoingBusinessAs%s'%n]],
            'Industry' : {
                'SICs' : [ { 'Code' : rec['IndustryCode%s'%n], 'Description' : rec['IndustryCodeDesc%s'%n] } for n in range(1,7) if rec['IndustryCode%s'%n]],
                'LineOfBusiness' : rec['LineOfBusiness'],
            },
            'CEO' : {
                'Name' : rec['CEOName'],
                'Title' : rec['CEOTitle'],
            },
            'AnnualSalesUSD' : int(Decimal(rec['AnnualSalesUSDollars'])) if rec['AnnualSalesUSDollars'] != '' else None,
            'StartYear' : int(rec['CompanyStartYear']) if rec['CompanyStartYear'] not in ('', '0000') else None,
            'ControlYear' : int(rec['ControlYear']) if rec['ControlYear'] not in ('', '0000') else None,
            'EmployeesTotal' : int(rec['EmployeesTotal']) if rec['EmployeesTotal'] not in ('', '0') else None,
            'EmployeesHere' : int(rec['EmployeesTotalHere']) if rec['EmployeesTotalHere'] not in ('', '0') else None,
            'LegalStatus' : rec['LegalStatus'],
            'FederalTaxID' : rec['FederalTaxID'],
            'NationalTaxID' : rec['NationalTaxID'],
            'NationalTaxIDInd' : rec['NationalTaxIDInd'],
            'SingleLocation' : rec['SingleLocation'] == 'true',
            }

    master.remove()
    for rec in db.Firmographics.find():
        rec = xform(rec)
        master.insert(rec)

    for rec in master.find({}, {'_id' : 1}):
        duns = rec['_id']

        addl = {}

        for coll_name, fields in maps.items():
            row = db[coll_name].find_one({'DUNSNumber' : duns})
            if row:
                for row_k, row_v in row.items():
                    addl[row_k] = row_v

        ww = { field : addl.get(field)  for field in addl_fields }
        master.update({'_id' : duns}, { '$set' : {'Addl' : ww } }, w=1)

        #TODO: add ensure index
    exit()


    duns = [r['DUNSNumber'] for r in db.Firmographics.find()]
#    duns = ['083542527']

    for idx, entity in enumerate(ENTITIES):
        coll = db[entity]
        cc = 0
        print 'working',
        for i, d in enumerate(duns):
            doc = coll.find_one({'DUNSNumber' : d}, {'_id' : 0})
            if doc:
                cc += 1
                if master.find_one({'_id': d}):
                    master.update({'_id' : d}, { '$set' : doc }, w=1)
                else:
                    doc['_id'] = d
                    master.insert(doc)
            if i%100==0:
                print '.',
        print entity, coll.count(), cc

def set_flags():
    conn = Connection('localhost')
    db = conn.hit
    for row in db.companies.find():
        flags = []
        if row['Addl']['WomanOwnedIndicator'] == 'Y':
            flags.append('woman')
        if row['Addl']['VeteranOwnedIndicator'] == 'Y':
            flags.append('veteran')
        if row['Addl']['MinorityIndicator'] == 'Y':
            flags.append('minority')
        if row['Addl']['GreenBusinessIndicator'] == 'Y':
            flags.append('green')
        db.companies.update({'_id' : row['_id']}, { '$set' : { 'Flags' : flags } }) 


def geocode():
    conn = Connection('localhost')
    db = conn.hit
    c = 0
    for row in db.companies.find({'Location.Latitude' : None}):
        loc = row['Location']
        addr = '%(Street1)s %(Street2)s %(City)s, %(State)s %(PostalCode)s %(Country)s' % loc
        resp = requests.get('http://maps.googleapis.com/maps/api/geocode/json', params={'address' : addr, 'sensor' : 'false'}).json()
        if resp['status'] == 'OK':
            print 'updating', row['_id']
            res = resp['results'][0]['geometry']
            doc = {
                'Latitude' : res['location']['lat'],
                'Longitude' : res['location']['lng'],
                'AccuracyCode' : res['location_type'],
            }
            db.companies.update({'_id' : row['_id']}, { '$set' : {'Location.Latitude' : doc['Latitude'], 'Location.Longitude': doc['Longitude'], 'Location.AccuracyCode' : doc['AccuracyCode'] } }, w=1)
        else:
            print 'error', resp
        sleep(0.1)
        c += 1
    print c

def geocode_bing():
    conn = Connection('localhost')
    db = conn.hit
    c = 0
    for row in db.companies.find({'Location.Latitude' : None}):
        loc = row['Location']
        print loc
        if loc['Country'] == 'UNITED STATES':
            loc['Country'] = 'US'
        else:
            continue
            loc['Country'] = ''
        url = ('http://dev.virtualearth.net/REST/v1/Locations/%(Country)s/%(State)s/%(PostalCode)s/%(City)s/%(Street1)s' % loc)
        try:
            resp = requests.get(url, params={'maxResults': 1, 'key': settings.BING_MAPS_API_KEY}).json()
            if len(resp['resourceSets']):
                lat,lng = resp['resourceSets'][0]['resources'][0]['point']['coordinates']
                doc = {
                    'Latitude' : lat,
                    'Longitude' : lng,
                    'AccuracyCode' : 'BING'
                }
                db.companies.update({'_id' : row['_id']}, { '$set' : {'Location.Latitude' : doc['Latitude'], 'Location.Longitude': doc['Longitude'], 'Location.AccuracyCode' : doc['AccuracyCode'] } }, w=1)
        except:
            print 'error'
            pass
        c+= 1


def describe_entities():
    conn = Connection('localhost')
    db = conn.hit
    all_keys = []
    for entity in ENTITIES:
        coll = db[entity]
        print entity, coll.count()
        row = coll.find_one(None, {'_id': 0})
#        print row.keys()
        for key in sorted(row.keys()):
            print '  ' + key
            all_keys += row.keys()
    all_keys = sorted(list(set(all_keys)))

    print
    print 'ALL'
    print all_keys
    print len(all_keys)

def loadsic():
  tsv = requests.get('http://www.census.gov/econ/cbp/download/sic88_97.txt').text
  lines = tsv.split('\r\n')
  lines = lines[1:]
  entries = [{'code': line[:4].replace('-', ''), 'name' : line[6:]} for line in lines if '\\' not in line]
  for e in entries:
      e['level'] = 4
      e['filter'] = e['code']
      while e['filter'][-1] == '0':
          e['filter'] = e['filter'][0:-1]
      if len(e['code'])==2:
          e['level'] = 1
      elif e['code'][2:4] == '00':
          e['level'] = 2
      elif e['code'][3] == '0':
          e['level'] = 3
  print len(entries)
  coll = _db().sic
  coll.remove()
  coll.insert(entries)

