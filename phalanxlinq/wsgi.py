import os,sys
sys.path.append( os.path.abspath( os.path.join(os.path.dirname(__file__), '..') ) )

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phalanxlinq.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()