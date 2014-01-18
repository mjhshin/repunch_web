from django.conf.urls import patterns, url

urlpatterns = patterns('apps.stores.views',
    url(r'^$', 'index', name='store_index'),
    url(r'^edit$', 'edit_store', name='store_edit'),
    url(r'^hours$', 'hours_preview', name='store_hours'),
    url(r'^set-active-location$', 'set_active_location', name='store_set_active_location'),
    
    url(r'^image-upload/(?P<store_location_id>.+)$', 'image_upload', name='store_image_upload'),
    url(r'^image-get/(?P<store_location_id>.+)$', 'image_get', name='store_image_get'),
    url(r'^image-crop/(?P<store_location_id>.+)$', 'image_crop', name='store_image_crop'),
    url(r'^edit-location/(?P<store_location_id>.+)$', 'edit_location', name='store_location_edit'),
    
    url(r'^settings$', 'settings', name='store_settings'),
    url(r'^settings/refresh$', 'refresh', 
                                name='refresh_retailer_pin'),  
                                
    url(r'^qoc48mxyz/deactivate$', 'deactivate', name='store_deactivate'),
    url(r'^qoc48mxyz/activate$', 'activate', name='store_activate'),
)

