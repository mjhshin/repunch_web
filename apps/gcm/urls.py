from django.conf.urls import patterns, url

urlpatterns = patterns('apps.gcm.views',
    url(r'^receive$', 'receive', name='gcm_receive'),
    
)

