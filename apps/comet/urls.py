from django.conf.urls import patterns, url

urlpatterns = patterns('apps.comet.views',
    url(r'^refresh$', 'refresh', name='comet_refresh'),
    url(r'^terminate$', 'terminate', name='comet_terminate'),
    url(r'^receive/(?P<store_id>.+)$', 'receive', name='comet_receive'),
    
)

