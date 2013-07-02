from django.conf.urls import patterns, url

urlpatterns = patterns('apps.comet.views',
    url(r'^$', 'refresh', name='comet_refresh'),
    url(r'^$', 'receive/(?P<store_id>.+)', name='comet_receive'),
)

