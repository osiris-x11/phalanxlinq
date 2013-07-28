from django.core.management.base import BaseCommand, CommandError
from web.rest import _db
import requests

class Command(BaseCommand):
    help = 'Load all data'

    def handle(self, *args, **options):
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


