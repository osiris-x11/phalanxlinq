from django.conf.urls.defaults import patterns, include, url
import views
import rest
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
#	url(r'^rest/dnb/(?P<dataset>.*)', rest.mongo_q, name='proxy'),
	url(r'^rest/dnb/(?P<dataset>.*)', rest.mongo_rest_proxy, name='proxy'),
#	url(r'^rest/dnb/(?P<dataset>.*)', rest.proxy, name='proxy'),
    url(r'^search$', views.search, name='search'),
    url(r'^$', direct_to_template, {'template': 'web/home.html'}, name='home'),
#	url(r'^companies', company_search, name='search'),
#	url(r'^forms/(?P<form_id>.*)/x-details', public.get_company_details, name='get_company_details'),
)
