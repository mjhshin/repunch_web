from django.conf.urls import patterns, url

urlpatterns = patterns('apps.rewards.views',
    url(r'^$', 'index', name='rewards_index'),
    url(r'^(?P<reward_id>.+)/edit$', 'edit', name='reward_edit'),
    url(r'^(?P<reward_id>.+)/avatar$', 'avatar', name='reward_avatar'),
    url(r'^(?P<reward_id>.+)/delete$', 'delete', name='reward_delete'),
)
