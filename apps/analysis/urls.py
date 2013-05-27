from django.conf.urls import patterns, url
from apps.analysis import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='analysis_index'),
    url(r'^trends/(?P<data_type>(punches|facebook|patrons))/(?P<start>\d{4}-\d{2}-\d{2})/(?P<end>\d{4}-\d{2}-\d{2})/$', views.trends_graph, name='trends_graph'),
    url(r'^breakdown/(?P<data_type>(punches|facebook|patrons))/(?P<filter>(.*))/(?P<range>(.*))/$', views.breakdown_graph, name='breakdown_graph'),
)