from django.conf.urls import patterns, url

urlpatterns = patterns('apps.analysis.views',
    url(r'^$', 'index', name='analysis_index'),
    url(r'^trends/(?P<data_type>(punches|facebook|patrons))/(?P<start>\d{4}-\d{2}-\d{2})/(?P<end>\d{4}-\d{2}-\d{2})/$', 'trends_graph', name='trends_graph'),
    url(r'^breakdown/(?P<data_type>(punches|facebook|patrons))/(?P<filter>(.*))/(?P<range>(.*))/$', 'breakdown_graph', name='breakdown_graph'),
)
