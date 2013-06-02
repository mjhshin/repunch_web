from django.conf.urls import patterns, url

urlpatterns = patterns('apps.messages.views',
    url(r'^$', 'index', name='messages_index'),
    url(r'^(?P<message_id>\d+)/edit', 'edit', name='message_edit'),
    url(r'^(?P<message_id>\d+)/delete', 'delete',
                                            name='message_delete'),
    url(r'^(?P<message_id>\d+)/duplicate', 'duplicate',
                                            name='message_duplicate'),
    url(r'^feedback/(?P<feedback_id>\d+)$', 'feedback',
                                            name='feedback_details'),
    url(r'^feedback/(?P<feedback_id>\d+)/reply$', 'feedback_reply',
                                            name='feedback_reply'),
    url(r'^feedback/(?P<feedback_id>\d+)/delete$', 'feedback_delete',
                                            name='feedback_delete')
)
