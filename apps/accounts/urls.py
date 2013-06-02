from django.conf.urls import patterns, url

urlpatterns = patterns('apps.accounts.views',
    url(r'^update', 'upgrade', name='account_upgrade'),
    url(r'^settings$', 'settings', name='account_settings'),
    url(r'^settings/refresh$', 'refresh', 
                                name='refresh_retailer_id'),   
 
)

