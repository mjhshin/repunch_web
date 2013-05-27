from django.conf.urls import patterns, url
from apps.stores import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='store_index'),
    url(r'^edit$', views.edit, name='store_edit'),
    url(r'^avatar$', views.avatar, name='store_avatar'),
    url(r'^hours$', views.hours_preview, name='store_hours'),

    
)

