from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.db.models import Sum
from datetime import datetime
import urllib, json

from parse.auth.decorators import login_required
from parse.apps.accounts.models import Account
from parse.apps.employees import PENDING, APPROVED, DENIED
from parse.apps.employees.models import Employee
from parse.apps.rewards.models import Punch
from apps.employees.forms import EmployeeForm, EmployeeAvatarForm
from libs.repunch import rputils


@login_required
def index(request):
    data = {'employees_nav': True}
    account = request.session['account']
    
    data['employees'] = Employee.objects().filter(Store=\
                        account.get('Store'), status=APPROVED)
    data['pending'] = Employee.objects().filter(Store=\
                        account.get('Store'), status=PENDING)
    
    data['show_pending'] = (request.GET.get("show_pending") is not None); 
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/employees.djhtml', data)

@login_required
def edit(request, employee_id):
    store = request.session['account'].get('store')
    data = {'employees_nav': True, 'employee_id': employee_id}
    
    #need to make sure this reward really belongs to this store
    employee = Employee.objects().get(Store=store.objectId,
                    objectId=employee_id)
    acc = Account.objects().get(Employee=employee.objectId)
    if not employee or not acc:
        raise Http404
    
    if request.method == 'POST': 
        # shouldn't go here, shin scrapped editing employee info
        form = EmployeeForm(request.POST)
        if form.is_valid(): 
            employee.update_locally(request.POST.dict(), False)
            employee.update()
            acc.set('email', request.POST['email'])
            acc.update()
            data['success'] = "Employee has been updated."
    else:
        if request.GET.get("success"):
            data['success'] = request.GET.get("success")
        if request.GET.get("error"):
            data['error'] = request.GET.get("error")
            
        form = EmployeeForm(employee.__dict__)
        form.data['email'] = acc.get('email')
    
    data['form'] = form
    data['employee'] = employee

    return render(request, 'manage/employee_edit.djhtml', data)

@login_required
def delete(request, employee_id):
    store = request.session['account'].get('store')

    #need to make sure this reward really belongs to this store
    employee = Employee.objects().get(Store=store.objectId,
                    objectId=employee_id)
    if not employee:
        raise Http404

    # TODO delete Punches and Rewards Pointers to this employee?
    employee.delete()

    return redirect(reverse('employees_index')+ "?%s" %\
        urllib.urlencode({'success': 'Employee has been deleted.'}))

@login_required
def approve(request, employee_id):
    store = request.session['account'].get('store')

    #need to make sure this reward really belongs to this store
    employee = Employee.objects().get(Store=store.objectId,
                    objectId=employee_id)
    if not employee:
        raise Http404
    
    employee.set('status', APPROVED)
    employee.update()
    
    return redirect(reverse('employees_index')+ "?show_pending&%s" %\
        urllib.urlencode({'success': 'Employee has been approved.'}))

@login_required
def deny(request, employee_id):
    store = request.session['account'].get('store')

    #need to make sure this reward really belongs to this store
    employee = Employee.objects().get(Store=store.objectId,
                    objectId=employee_id)
    if not employee:
        raise Http404
    
    employee.status = DENIED;
    employee.update();
    
    return redirect(reverse('employees_index')+ "?show_pending&%s" %\
        urllib.urlencode({'success': 'Employee has been denied.'}))

@login_required
def avatar(request, employee_id):
    employee_id = int(employee_id)
    data = {}
    employee = None
    store = request.session['account'].store
    
    # need to make sure this reward really belongs to this store
    if(employee_id > 0):
        try:
            employee = Employee.objects.filter(store=store.id).get(id=employee_id)
        except Employee.DoesNotExist:
            raise Http404
    else:
        raise Http404
    
    if request.method == 'POST': # If the form has been submitted...
        form = EmployeeAvatarForm(request.POST, request.FILES, instance=employee) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            form.save()
            data['success'] = True
    else:
        form = EmployeeAvatarForm();
    
    data['form'] = form
    data['url'] = reverse('employee_avatar', args=[employee_id])
    return render(request, 'manage/avatar_upload.djhtml', data)

@login_required
def punches(request, employee_id):
    from apps.rewards.models import Punch

    employee_id = int(employee_id)
    store = request.session['account'].store
    employee = None
    data = {'employee_id': employee_id}
    
    if(employee_id > 0):
        try:
            employee = Employee.objects.filter(store=store.id).get(id=employee_id)
        except Employee.DoesNotExist:
            raise Http404
    else:
        raise Http404
    
    order_by = request.POST.get('order_by')
    if order_by == None:
        order_by = 'date_punched'
    
    if order_by == 'customer':
        order_by = 'patron'
    
    order_dir = request.POST.get('order_dir')
    if order_dir != None and order_dir.lower() == 'desc':
        order_by = '-'+order_by
    
    
    paginator = Paginator(Punch.objects.filter(employee_id=employee.id).order_by(order_by), 12)
    
    page = request.GET.get('page')
    try:
        punches = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        punches = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        punches = paginator.page(paginator.num_pages)
    
    data['punches'] = punches
    
    return render(request, 'manage/employee_punches.djhtml', data)

@login_required
def graph(request):
    employee_ids = request.GET.getlist('employee[]')
    start = request.GET.get('start')
    end = request.GET.get('end');
    
    start = datetime.strptime(start, "%m/%d/%Y")
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = datetime.strptime(end, "%m/%d/%Y")
    end = end.replace(hour=23, minute=59, second=59, microsecond=0)
    
    columns = [
                {"id":"", "label":"Date", "type":"string"}
               ]
    employees = Employee.objects().filter(objectId=employee_ids)
    for emp in employees:
        columns.append({"id":"", "label":emp.first_name+' '+emp.last_name, "type":"number"})

    punch_map = {}
    punches = Punch.objects.extra(select={'myd': "date(date_punched)"}).values('myd', 'employee').filter(date_punched__range=(start, end),employee_id__in=employees).annotate(num_punches=Sum('punches'))
    
    #create dictionary for easy search
    for punch in punches:
        punch_map[punch['myd'].strftime("%m/%d")+'-'+str(punch['employee'])] = punch['num_punches'] 

    rows = []
    for single_date in rputils.daterange(start, end):
        str_date = single_date.strftime("%m/%d")
        c = [{"v": str_date}]
        for emp in employees:
            try:
                punch_count = punch_map[str_date + '-' + str(emp.id)]
            except KeyError:
                punch_count = 0
                
            c.append({"v": punch_count})
        rows.append({'c': c})
        
    return HttpResponse(json.dumps({'cols': columns, 'rows': rows}), content_type="application/json")
