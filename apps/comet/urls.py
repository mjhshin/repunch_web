from django.conf.urls import patterns, url

urlpatterns = patterns('apps.comet.views',
    url(r'^pull$', 'pull', name='comet_pull'),
    url(r'^terminate$', 'terminate', name='comet_terminate'),
    url(r'^receive/(?P<store_id>.+)$', 'receive', name='comet_receive'),
    
)

