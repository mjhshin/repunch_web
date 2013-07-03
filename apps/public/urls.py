from django.conf.urls import patterns, url

urlpatterns = patterns('apps.public.views',
    # public URLS
    url(r'^$', 'index', name='public_home'),
    url(r'^learn/$', 'learn', name='public_learn'),
    url(r'^faq/$', 'faq', name='public_faq'),
    url(r'^about/$', 'about', name='public_about'),
    url(r'^signup/$', 'sign_up', name='public_signup'),
    url(r'^signup-2/$', 'sign_up2', name='public_signup2'),
    url(r'^terms/$', 'terms', name='public_terms'),
    # url(r'^mobile-terms/$', 'privacy', name='public_mobile_terms'),
    url(r'^privacy/$', 'privacy', name='public_privacy'),
    # url(r'^mobile-privacy/$', 'privacy', name='public_mobile_privacy'),
    url(r'^contact/$', 'contact', name='public_contact'),
    url(r'^contact/thank_you/$', 'thank_you', name='public_thank_you'),
    url(r'^jobs/$', 'jobs', name='public_jobs'),
    url(r'^categories/$', 'categories', name='public_categories'),
    
    url(r'^requestPasswordReset/$', 'password_reset', name='public_request_password_reset'),
)
