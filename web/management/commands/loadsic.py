from django.core.management.base import BaseCommand, CommandError
from web.rest import _db
import requests

class Command(BaseCommand):
    help = 'Load all data'

    def handle(self, *args, **options):
        tsv = requests.get('http://www.census.gov/econ/cbp/download/sic88_97.txt').text
        lines = tsv.split('\r\n')
        lines = lines[1:]
        entries = [{'code': line[:4].replace('-', '0').replace('\\', '0'), 'name' : line[6:]} for line in lines]
        print len(entries)
        coll = _db().sic
        coll.remove()
        coll.insert(entries)


