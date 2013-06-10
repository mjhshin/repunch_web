from django.conf.urls import patterns, url

urlpatterns = patterns('apps.messages.views',
    url(r'^$', 'index', name='messages_index'),
    url(r'^(?P<message_id>\w+)/edit', 'edit', name='message_edit'),
    url(r'^(?P<message_id>\w+)/delete', 'delete',
                                            name='message_delete'),
    url(r'^(?P<message_id>\w+)/details', 'details',
                                            name='message_details'),
    url(r'^feedback/(?P<feedback_id>\w+)$', 'feedback',
                                            name='feedback_details'),
    url(r'^feedback/(?P<feedback_id>\w+)/reply$', 'feedback_reply',
                                            name='feedback_reply'),
    url(r'^feedback/(?P<feedback_id>\w+)/delete$', 'feedback_delete',
                                            name='feedback_delete')
)
