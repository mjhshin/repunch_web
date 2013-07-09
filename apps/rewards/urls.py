from django.conf.urls import patterns, url

urlpatterns = patterns('apps.rewards.views',
    url(r'^$', 'index', name='rewards_index'),
    url(r'^(?P<reward_index>.+)/edit$', 'edit', name='reward_edit'),
    url(r'^(?P<reward_index>.+)/delete$', 'delete', name='reward_delete'),
)
