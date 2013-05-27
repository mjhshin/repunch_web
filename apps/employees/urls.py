from django.conf.urls import patterns, url
from apps.employees import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='employees_index'),
    url(r'^graph$', views.graph, name='employee_graph'),
    url(r'^(?P<employee_id>\d+)/edit', views.edit, name='employee_edit'),
    url(r'^(?P<employee_id>\d+)/delete', views.delete, name='employee_delete'),
    url(r'^(?P<employee_id>\d+)/approve', views.approve, name='employee_approve'),
    url(r'^(?P<employee_id>\d+)/deny', views.deny, name='employee_deny'),
    url(r'^(?P<employee_id>\d+)/avatar$', views.avatar, name='employee_avatar'),
    url(r'^(?P<employee_id>\d+)/punches$', views.punches, name='employee_punches'),
)