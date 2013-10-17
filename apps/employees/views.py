from django.shortcuts import render, redirect
from django.contrib.sessions.backends.cache import SessionStore
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
import urllib, json

from parse.utils import make_aware_to_utc
from parse.apps.employees import DENIED, APPROVED, PENDING
from parse import session as SESSION
from parse.comet import comet_receive
from parse.utils import cloud_call
from parse.decorators import access_required, admin_only
from parse.auth.decorators import login_required, dev_login_required
from parse.apps.accounts.models import Account
from parse.apps.employees.models import Employee
from parse.apps.rewards.models import Punch
from parse.apps.stores import ACCESS_ADMIN, ACCESS_PUNCHREDEEM,\
ACCESS_NONE
from apps.employees.forms import EmployeeForm
from apps.accounts.forms import AccountSignUpForm
from apps.accounts.models import AssociatedAccountNonce
from libs.repunch import rputils
from repunch.settings import COMET_RECEIVE_KEY_NAME,\
COMET_RECEIVE_KEY, PAGINATION_THRESHOLD

@dev_login_required
@login_required
@access_required
def index(request):
    data = {'employees_nav': True}
    
    data['pending'] =\
            SESSION.get_employees_pending_list(request.session)
    data['employees'] =\
            SESSION.get_employees_approved_list(request.session)
    
    data['show_pending'] = (request.GET.get("show_pending") is not None); 
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/employees.djhtml', data)

@dev_login_required
@login_required
@admin_only(reverse_url="employees_index")
def edit(request, employee_id):
    data = {'employees_nav': True, 'employee_id': employee_id}
    
    # get from the employees_approved_list in session cache
    employees_approved_list = SESSION.get_employees_approved_list(\
        request.session)
    employee = None
    for m in employees_approved_list:
        if m.objectId == employee_id:
            employee = m
            break
            
    acc = Account.objects().get(Employee=employee.objectId)
    store = SESSION.get_store(request.session)
            
    if not employee or not acc:
        return redirect(reverse('employees_index')+ "?%s" %\
            urllib.urlencode({'success': 'Employee does not exist.'}))

    if request.method == "POST":
        store.set_access_level(acc, request.POST["ACL"])
                
        store.update()
        request.session['store'] = store
        # notify other dashboards of this change
        payload = {
            COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
            "updatedStore":store.jsonify()
        }
        comet_receive(store.objectId, payload)
        
        return redirect(reverse('employees_index')+ "?%s" %\
            urllib.urlencode({'success': 'Employee has been updated.'}))
        
    form = EmployeeForm(employee.__dict__.copy())
    form.data['email'] = acc.get('email')
    
    data.update({
        'ACCESS_ADMIN': ACCESS_ADMIN[0],
        'ACCESS_PUNCHREDEEM': ACCESS_PUNCHREDEEM[0],
        'ACCESS_NONE': ACCESS_NONE[0],
        'form': form,
        'employee': employee,
        'employee_acl': store.get_access_level(acc)[0],
    })

    return render(request, 'manage/employee_edit.djhtml', data)

@dev_login_required
@login_required
@admin_only(reverse_url="employees_index")
def delete(request, employee_id):
    """ 
    This will also remove the employee from the ACL,
    delete the employee object and also delete the Parse.User object
    if and only if it has no pointer to a Store or a Patron.
    """
    # get from the employees_approved_list in session cache
    employees_approved_list = SESSION.get_employees_approved_list(\
        request.session)
    i_remove, employee = 0, None
    for ind, m in enumerate(employees_approved_list):
        if m.objectId == employee_id:
            employee = m
            i_remove = ind
            break
            
    if not employee:
        return redirect(reverse('employees_index')+ "?%s" %\
            urllib.urlencode({'success': 'Employee has already been removed.'}))

    employees_approved_list.pop(i_remove)   
    request.session['employees_approved_list'] =\
        employees_approved_list
        
    acc = Account.objects().get(Employee=employee.objectId)
    if not acc: # employee may have been deleted
        return redirect(reverse('employees_index')+ "?%s" %\
            urllib.urlencode({'success': 'Employee has already been deleted.'}))
        
    # Always save session first whenever calling a cloud code
    request.session.save()
    
    res = cloud_call("delete_employee", {"employee_id": employee.objectId})
    
    request.session.clear()
    request.session.update(SessionStore(request.session.session_key))
    
    if 'error' not in res:
        store = SESSION.get_store(request.session)
        payload = { COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY }
        if acc.objectId in store.ACL and not store.is_owner(acc):
            del store.ACL[acc.objectId]
            store.update()
            payload["updatedStore"] = store.jsonify()
            request.session['store'] = store
            
        # only need to pass in the objectId
        deleted_employee = Employee(objectId=employee.objectId)
        payload["deletedEmployee"] = deleted_employee.jsonify()
            
        comet_receive(store.objectId, payload)

        return redirect(reverse('employees_index')+ "?%s" %\
            urllib.urlencode({'success': 'Employee has been deleted.'}))
                
    return redirect(reverse('employees_index')+ "?%s" %\
        urllib.urlencode({'success': 'Employee has already been deleted.'}))
    

@dev_login_required
@login_required
@admin_only(reverse_url="employees_index")
def approve(request, employee_id):
    # get from the employees_pending_list in session cache
    employees_pending_list = SESSION.get_employees_pending_list(\
        request.session)
    i_remove, employee = 0, None
    for ind, m in enumerate(employees_pending_list):
        if m.objectId == employee_id:
            employee = m
            i_remove = ind
            break
            
    if not employee:
        return redirect(reverse('employees_index')+ "?%s" %\
            urllib.urlencode({'success': 'Pending employee not found.'}))
    
    employee.set('status', APPROVED)
    employee.update()
            
    employees_pending_list.pop(i_remove)
    request.session['employees_pending_list'] =\
        employees_pending_list
    
    # update session cache for employees_approved_list
    employees_approved_list = SESSION.get_employees_approved_list(\
        request.session)
    employees_approved_list.insert(0, employee)
    request.session['employees_approved_list'] =\
        employees_approved_list
        
    # notify other dashboards of this change
    store_id = SESSION.get_store(request.session).objectId
    approved_employee = Employee(objectId=employee.objectId)
    payload = {
        COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
        "approvedEmployee":approved_employee.jsonify()
    }
    comet_receive(store_id, payload)
        
    return redirect(reverse('employees_index')+ "?show_pending&%s" %\
        urllib.urlencode({'success': 'Employee has been approved.'}))

@dev_login_required
@login_required
@admin_only(reverse_url="employees_index")
def deny(request, employee_id):
    """ same as delete except this uses the pending list """
    # get from the employees_pending_list in session cache
    employees_pending_list = SESSION.get_employees_pending_list(\
        request.session)
    i_remove, employee = 0, None
    for ind, m in enumerate(employees_pending_list):
        if m.objectId == employee_id:
            employee = m
            i_remove = ind
            break
            
    if not employee:
        return redirect(reverse('employees_index')+ "?%s" %\
            urllib.urlencode({'success': 'Pending employee not found.'}))
    
    # update session cache for employees_pending_list
    employees_pending_list.pop(i_remove)
    request.session['employees_pending_list'] =\
        employees_pending_list
        
        
    acc = Account.objects().get(Employee=employee.objectId)
    if not acc: # employee may have been deleted
        return redirect(reverse('employees_index')+ "?show_pending&%s" %\
            urllib.urlencode({'success': 'Employee has already been denied.'}))
        
    # Always save session first whenever calling a cloud code
    request.session.save()
    
    res = cloud_call("delete_employee", {"employee_id": employee.objectId})
    
    request.session.clear()
    request.session.update(SessionStore(request.session.session_key))
    
    if 'error' not in res:
        payload = { COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY }
        store = SESSION.get_store(request.session)
        # no need to check acl here but just in case
        if acc.objectId in store.ACL and not store.is_owner(acc):
            del store.ACL[acc.objectId]
            store.update()
            payload["updatedStore"] = store.jsonify()
            request.session['store'] = store
            
        # only need to pass in the objectId
        deleted_employee = Employee(objectId=employee.objectId)
        payload["deletedEmployee"] = deleted_employee.jsonify()
            
        comet_receive(store.objectId, payload)
    
        return redirect(reverse('employees_index')+ "?show_pending&%s" %\
            urllib.urlencode({'success': 'Employee has been denied.'}))
                
    return redirect(reverse('employees_index')+ "?%s" %\
        urllib.urlencode({'success': 'Employee has already been deleted.'}))

@dev_login_required
@login_required
@access_required(http_response="Access Denied", content_type="text/plain")
def punches(request, employee_id):
    data = {'employee_id': employee_id}
    
    # get from the employees_approved_list in session cache
    employees_approved_list = SESSION.get_employees_approved_list(\
        request.session)
    employee = None
    for ind, m in enumerate(employees_approved_list):
        if m.objectId == employee_id:
            employee = m
            break
            
    if not employee:
        raise Http404
    
    # page starts at 1
    page = int(request.GET.get('page'))
    order_by = request.POST.get('order_by')
    order_dir = request.POST.get('order_dir')
    if order_dir != None and order_dir.lower() == 'desc':
        order_by = '-'+order_by
        
    # limit is +1 to find out if has_next
    limit = PAGINATION_THRESHOLD + 1
    skip = (page-1) * PAGINATION_THRESHOLD
    
    employee.set("punches", None)
    punches = employee.get('punches', order=order_by,
        limit=limit, skip=skip)
        
    # make sure to pop the PAGINATION_THRESHOLD + 1 row if exist
    if punches and len(punches) > PAGINATION_THRESHOLD:
        punches.pop()
        data['next_page_number'] = page + 1
        
    data['punches'] = punches
    
    return render(request, 'manage/employee_punches.djhtml', data)

@dev_login_required
@login_required
@access_required(http_response={"error": "Access denied"})
def graph(request):
    store_timezone = SESSION.get_store_timezone(request.session)
    
    employee_ids = request.GET.getlist('employee[]')
    start = request.GET.get('start')
    end = request.GET.get('end');
    
    start = datetime.strptime(start, "%m/%d/%Y")
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = datetime.strptime(end, "%m/%d/%Y")
    end = end.replace(hour=23, minute=59, second=59, microsecond=0)
    
    # need to make aware and then convert to utc for querying
    start_aware = make_aware_to_utc(start, store_timezone)
    end_aware = make_aware_to_utc(end, store_timezone)
    
    columns = [
                {"id":"", "label":"Date", "type":"string"}
               ]
               
    # build the list of employees from the list in the session cache
    employees_approved_list = SESSION.get_employees_approved_list(\
        request.session)
    employees = []
    for ind, m in enumerate(employees_approved_list):
        if m.objectId in employee_ids:
            employees.append(m)
    
    if employees:
        for emp in employees:
            columns.append({"id":"", "label":emp.get('first_name')+\
                    ' '+emp.get('last_name'), "type":"number"})
  
    punch_map = {}
    # since a punch no longer contains a pointer to an employee
    # the query must be made in the punches for each employee...
    if employees:
        for emp in employees:
            ps =  emp.get('punches', createdAt__gte=start_aware, 
                createdAt__lte=end_aware)
            if ps:
                for punch in ps:
                    key = timezone.localtime(punch.createdAt,
                        store_timezone).strftime("%m/%d")+'-'+\
                        emp.objectId
                    if key in punch_map: 
                        punch_map[key] = punch_map[key] +\
                                    punch.get('punches')
                    else:
                        punch_map[key] = punch.get('punches')


    rows = []
    for single_date in rputils.daterange(start, end):
        str_date =  make_aware_to_utc(single_date,
            store_timezone).strftime("%m/%d")
        c = [{"v": str_date}]
        for emp in employees:
            try:
                punch_count = punch_map[str_date + '-' + emp.objectId]
            except KeyError:
                punch_count = 0
            c.append({"v": punch_count})
        rows.append({'c': c})

    return HttpResponse(json.dumps({'cols': columns, 'rows': rows}), content_type="application/json")
    
    
@dev_login_required
@login_required
@admin_only(reverse_url="employees_index")
def register(request):
    """ 
    Adds a new employee to the currently logged in Store.
    This automatically sets this employee to approved.
    """
    data = {'employees_nav': True}
    if request.method == "POST":
        from_associated_account = False
        # check if this post is from the associated account dialog
        # if it is then skip form validations
        aaf_nonce_id = request.POST.get('aaf-nonce')
        aaf_account_id = request.POST.get('aaf-account_id')
        if len(aaf_nonce_id) > 0 and len(aaf_account_id) > 0:
            aa_nonce = AssociatedAccountNonce.objects.filter(\
                id=aaf_nonce_id, account_id=aaf_account_id)
            if len(aa_nonce) > 0 and aa_nonce[0].verified:
                aa_nonce[0].delete()
                from_associated_account = True
        
        account_form = AccountSignUpForm(request.POST)
        employee_form = AccountSignUpForm(request.POST)
        
        if not from_associated_account:
            all_forms_valid = account_form.is_valid() and\
                employee_form.is_valid()
        else:
            all_forms_valid = True
            
        if all_forms_valid:
            postDict = request.POST.dict()
            # check if email already taken here to handle the case where 
            # the user already has a patron/employee account 
            # but also want to sign up for a Store account
            if hasattr(account_form, "associated_account"):
                aa = account_form.associated_account
                aan = AssociatedAccountNonce.objects.create(\
                    account_id=aa.objectId)
                return HttpResponse(json.dumps({"associated_account":\
                    aa.objectId, "associated_account_nonce":aan.id,
                    "email": aa.email, "code": 0}), 
                    content_type="application/json")
                  
            # TODO
            
            return HttpResponse(json.dumps({}), 
                        content_type="application/json") 
                
    else:
        employee_form = EmployeeForm(initial={"acl":\
            ACCESS_PUNCHREDEEM[0]})
        account_form = AccountSignUpForm()
        
    data["employee_form"] = employee_form
    data["account_form"] = account_form
        
    return render(request, 'manage/employee_register.djhtml', data)    
    
@dev_login_required
@login_required
@admin_only(reverse_url="employees_index")
def associated_account_confirm(request):
    """
    A helper view for sign_up. Also handles requests from signup.js
    """
    if request.method == 'POST':
        # first check the AssociatedAccountNonce
        acc_id = request.POST['aaf-account_id']
        nonce_id = request.POST['aaf-nonce']
        aa_nonce = AssociatedAccountNonce.objects.filter(\
            id=nonce_id, account_id=acc_id)
        if len(aa_nonce) > 0:
            aa_nonce = aa_nonce[0]
            # then attempt to login to parse
            username = request.POST['acc_username']
            password = request.POST['acc_password']
            # note that email is the same as username
            res = account_login(username, password)
            if 'error' not in res:
                aa_nonce.verified = True
                aa_nonce.save()
                return HttpResponse(json.dumps({"code": 0}), 
                    content_type="application/json")
                
    return HttpResponse(json.dumps({"code": 1}), 
        content_type="application/json")

@dev_login_required
@login_required
def avatar(request, employee_id):
    """
    Unused at the moment.
    """
    """
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
    """
    raise Http404

