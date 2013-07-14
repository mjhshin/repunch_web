from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth import logout
import json, thread

from parse import session as SESSION
from parse.auth import login
from apps.accounts.forms import LoginForm
from apps.comet.models import CometSession

def manage_password_reset(request):
    """ Displays the password reset template """
    return render(request, 'manage/choose_password.html')
    

def manage_password_reset_complete(request):
    """ Displays the password reset complete template """
    return render(request, 'manage/password_updated.html')

def manage_login(request):
    """
    Handle s ajax request from login-dialog.
    returns a json object with a code.
    Or renders the dedicated login page if manually enterd url.
    code 
       -1 - invalid request
        0 - invalid form input
        1 - bad login credentials
        2 - subscription is not active
        3 - success
    """
    data = {"code":-1}
    if request.method == 'POST' or request.is_ajax():
        form = LoginForm(request.POST)
        if form.is_valid(): 
            c = login(request, request.POST.dict().copy())
            c_type = type(c)
            if c_type is int:
                if c == 0:
                    data['code'] = 1 
                elif c == 1:
                    data['code'] = 2
            else:
                data['code'] = 3
                # create the session comet here if it does not exist
                try: # attempt to get a used CometSession first
                    CometSession.objects.get(session_key=\
                        request.session.session_key)
                except CometSession.DoesNotExist:
                    scomet = CometSession.objects.create(session_key=\
                            request.session.session_key,
                            store_id=SESSION.get_store(\
                            request.session).objectId)
                            
        else:
            data['code'] =  0        
    else:
        if request.session.get('account'):
            return redirect(reverse('store_index'))
        data['form'] = LoginForm()
        return render(request, 'manage/login.djhtml', data)

    return HttpResponse(json.dumps(data), 
        content_type="application/json")

def manage_logout(request):
    # need to clear the session
    request.session.flush()
    return redirect(reverse('public_home'))

def manage_terms(request):
    return render(request, 'manage/terms.djhtml')

