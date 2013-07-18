from django.conf.urls.defaults import patterns, include, url
from views import *
import rest
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
	url(r'^rest/dnb/(?P<dataset>.*)', rest.proxy, name='proxy'),
#    url(r'^docs', direct_to_template, {'template': 'admin/leadform/docs.html'}, name='docs'),
#	url(r'^companies', company_search, name='search'),
#	url(r'^forms/(?P<form_id>.*)/x-details', public.get_company_details, name='get_company_details'),
)
