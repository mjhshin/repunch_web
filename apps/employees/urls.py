from django.conf.urls import patterns, url

urlpatterns = patterns('apps.employees.views',
    url(r'^$', 'index', name='employees_index'),
    url(r'^graph$', 'graph', name='employee_graph'),
    url(r'^(?P<employee_id>.+)/edit$', 'edit', name='employee_edit'),
    url(r'^(?P<employee_id>.+)/delete$', 'delete', name='employee_delete'),
    url(r'^(?P<employee_id>.+)/approve$', 'approve', name='employee_approve'),
    url(r'^(?P<employee_id>.+)/deny$', 'deny', name='employee_deny'),
    url(r'^(?P<employee_id>.+)/punches$', 'punches', name='employee_punches'),
    
    url(r'^register$', 'register', name='employee_register'),
    url(r'^associated-account-confirm$', 'associated_account_confirm', name='employee_associated_account_confirm'),
)
