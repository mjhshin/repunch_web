from django.conf.urls import patterns, url

urlpatterns = patterns('apps.stores.views',
    url(r'^$', 'index', name='store_index'),
    url(r'^edit$', 'edit_store', name='store_edit'),
    url(r'^hours$', 'hours_preview', name='store_hours'),
    url(r'^set-active-location$', 'set_active_location', name='store_set_active_location'),
    
    url(r'^avatar-upload/(?P<store_location_id>.+)$', 'avatar_upload', name='store_avatar_upload'),
    url(r'^get-avatar/(?P<store_location_id>.+)$', 'get_avatar', name='store_get_avatar'),
    url(r'^crop-avatar/(?P<store_location_id>.+)$', 'crop_avatar', name='store_crop_avatar'),
    url(r'^edit-location/(?P<store_location_id>.+)$', 'edit_location', name='store_location_edit'),
    
    url(r'^settings$', 'settings', name='store_settings'),
    url(r'^settings/refresh$', 'refresh', 
                                name='refresh_retailer_pin'),  
                                
    url(r'^qoc48mxyz/deactivate$', 'deactivate', name='store_deactivate'),
    url(r'^qoc48mxyz/activate$', 'activate', name='store_activate'),
)

