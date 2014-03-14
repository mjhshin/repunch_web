from django.conf.urls import patterns, url

urlpatterns = patterns('apps.dev_guide.views',
    url(r'^$', 'index', name='devguide_index'),
)
