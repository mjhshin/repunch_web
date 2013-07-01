from django.conf.urls import patterns, url

urlpatterns = patterns('apps.comet.views',
    url(r'^$', 'refresh', name='comet_refresh'),
)

