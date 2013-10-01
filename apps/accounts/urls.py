from django.conf.urls import patterns, url

urlpatterns = patterns('apps.accounts.views',
    url(r'^subscription/update$', 'update_subscription', name='subscription_update'), 
    
    url(r'^edit$', 'edit', name='account_edit'), 
    url(r'^edit/change-email$', 'change_email', name='account_change_email'),
    url(r'^edit/change-password$', 'change_password', name='account_change_password'),
 
)

