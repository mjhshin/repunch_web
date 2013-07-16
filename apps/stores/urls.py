from django.conf.urls import patterns, url

urlpatterns = patterns('apps.stores.views',
    url(r'^$', 'index', name='store_index'),
    url(r'^edit$', 'edit', name='store_edit'),
    url(r'^avatar$', 'avatar', name='store_avatar'),
    url(r'^hours$', 'hours_preview', name='store_hours'),
    url(r'^punch$', 'punch', name='store_punch'),
    
    url(r'^get-avatar$', 'get_avatar', name='store_get_avatar'),
    url(r'^crop-avatar$', 'crop_avatar', name='store_crop_avatar'),
    
)

