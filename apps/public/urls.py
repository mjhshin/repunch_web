from django.conf.urls import patterns, url
from apps.public import views

urlpatterns = patterns('',
    # public URLS
    url(r'^$', views.index, name='public_home'),
    url(r'^learn/$', views.learn, name='public_learn'),
    url(r'^faq/$', views.faq, name='public_faq'),
    url(r'^about/$', views.about, name='public_about'),
    url(r'^signup/$', views.sign_up, name='public_signup'),
    url(r'^terms/$', views.terms, name='public_terms'),
    url(r'^privacy/$', views.privacy, name='public_privacy'),
    url(r'^contact/$', views.contact, name='public_contact'),
    url(r'^contact/thank_you/$', views.thank_you, name='public_thank_you'),
    url(r'^jobs/$', views.jobs, name='public_jobs'),
    
)
