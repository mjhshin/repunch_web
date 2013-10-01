from django.conf.urls import patterns, url

urlpatterns = patterns('apps.accounts.views',
    url(r'^qoc48mxyz/deactivate', 'deactivate', name='account_deactivate'),
    url(r'^activate', 'activate', name='account_activate'),
    url(r'^subscription/update', 'update_subscription', name='subscription_update'), 
 
)

