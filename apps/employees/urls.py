from django.conf.urls import patterns, url

urlpatterns = patterns('apps.employees.views',
    url(r'^$', 'index', name='employees_index'),
    url(r'^graph$', 'graph', name='employee_graph'),
    url(r'^(?P<employee_id>\d+)/edit', 'edit', name='employee_edit'),
    url(r'^(?P<employee_id>\d+)/delete', 'delete', name='employee_delete'),
    url(r'^(?P<employee_id>\d+)/approve', 'approve', name='employee_approve'),
    url(r'^(?P<employee_id>\d+)/deny', 'deny', name='employee_deny'),
    url(r'^(?P<employee_id>\d+)/avatar$', 'avatar', name='employee_avatar'),
    url(r'^(?P<employee_id>\d+)/punches$', 'punches', name='employee_punches'),
)
