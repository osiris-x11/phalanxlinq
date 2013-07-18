from django.core.management.base import BaseCommand, CommandError
from web.rest import populate_mongo

class Command(BaseCommand):
    help = 'Load all data'

    def handle(self, *args, **options):
        populate_mongo()
