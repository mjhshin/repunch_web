from django.conf.urls import patterns, url
from apps.accounts import views

urlpatterns = patterns('',
    url(r'^update', views.upgrade, name='account_upgrade'),
    url(r'^settings$', views.settings, name='account_settings'),
    url(r'^settings/refresh$', views.refresh, name='refresh_retailer_id'),    
)

