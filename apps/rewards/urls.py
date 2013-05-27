from django.conf.urls import patterns, url
from apps.rewards import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='rewards_index'),
    url(r'^(?P<reward_id>\d+)/edit$', views.edit, name='reward_edit'),
    url(r'^(?P<reward_id>\d+)/avatar$', views.avatar, name='reward_avatar'),
    url(r'^(?P<reward_id>\d+)/delete$', views.delete, name='reward_delete'),    
)