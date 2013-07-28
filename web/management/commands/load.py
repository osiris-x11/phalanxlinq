from django.core.management.base import BaseCommand, CommandError
from web.rest import populate_mongo, describe_entities, consolidate, geocode

class Command(BaseCommand):
    help = 'Load all data'

    def handle(self, *args, **options):
        fn_map = {
            'populate' : populate_mongo,
            'list' : describe_entities,
            'consolidate' : consolidate,
            'geocode' : geocode,
        }
        fn = fn_map.get( (args + (None,))[0]  )
        if fn:
            fn()
        else:
            print 'Available commands: %s' % fn_map.keys()
