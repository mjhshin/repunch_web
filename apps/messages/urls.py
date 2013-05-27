from django.conf.urls import patterns, url
from apps.messages import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='messages_index'),
    url(r'^(?P<message_id>\d+)/edit', views.edit, name='message_edit'),
    url(r'^(?P<message_id>\d+)/delete', views.delete, name='message_delete'),
    url(r'^(?P<message_id>\d+)/duplicate', views.duplicate, name='message_duplicate'),
    url(r'^feedback/(?P<feedback_id>\d+)$', views.feedback, name='feedback_details'),
    url(r'^feedback/(?P<feedback_id>\d+)/reply$', views.feedback_reply, name='feedback_reply'),
    url(r'^feedback/(?P<feedback_id>\d+)/delete$', views.feedback_delete, name='feedback_delete')
)