from django.conf.urls import patterns, url

urlpatterns = patterns('apps.tutorials.views',
    url(r'^$', 'index', name='tutorials_index'),
)
