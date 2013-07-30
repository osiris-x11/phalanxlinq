from django.core.management.base import BaseCommand, CommandError
from web.loader import populate_mongo, describe_entities, consolidate, geocode, set_flags, loadsic, geocode_bing

class Command(BaseCommand):
    help = 'Load all data'

    def handle(self, *args, **options):
        fn_map = {
            'populate' : populate_mongo,
            'list' : describe_entities,
            'consolidate' : consolidate,
            'geocode' : geocode,
            'geocode-bing' : geocode_bing,
            'flags' : set_flags,
            'loadsic': loadsic,
        }
        fn = fn_map.get( (args + (None,))[0]  )
        if fn:
            fn()
        else:
            print 'Available commands: %s' % fn_map.keys()
