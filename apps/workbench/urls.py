from django.conf.urls import patterns, url

urlpatterns = patterns('apps.workbench.views',
    url(r'^$', 'index', name='workbench_index'),
    
)

