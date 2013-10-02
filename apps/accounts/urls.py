from django.conf.urls import patterns, url

urlpatterns = patterns('apps.accounts.views',
    url(r'^subscription/update$', 'update_subscription', name='subscription_update'), 
    
    url(r'^edit$', 'edit', name='account_edit'), 
 
)

