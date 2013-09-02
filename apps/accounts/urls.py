from django.conf.urls import patterns, url

urlpatterns = patterns('apps.accounts.views',
    url(r'^super-secret-url-prefix/deactivate', 'deactivate', name='account_deactivate'),
    url(r'^activate', 'activate', name='account_activate'),
    url(r'^upgrade', 'upgrade', name='account_upgrade'),
    url(r'^update', 'update', name='account_update'),
    url(r'^settings$', 'settings', name='account_settings'),
    url(r'^settings/refresh$', 'refresh', 
                                name='refresh_retailer_pin'),   
 
)

