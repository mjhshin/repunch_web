from django.shortcuts import redirect, render
from django.db import IntegrityError
from django.contrib.sessions.backends.cache import SessionStore
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import logout
import json, thread

from parse import session as SESSION
from parse.decorators import session_comet
from parse.auth import login
from apps.accounts.forms import LoginForm
from apps.comet.models import CometSession, CometSessionIndex

@session_comet
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
                # user may try to login on another tab when already in
                try:
                    CometSessionIndex.objects.create(session_key=\
                        request.session.session_key, datetime=\
                            timezone.now())
                except IntegrityError:
                    pass
                            
        else:
            data['code'] =  0        
    else:
        if request.session.get('account'):
            return redirect(reverse('store_index'))
        data['form'] = LoginForm()
        return render(request, 'manage/login.djhtml', data)

    return HttpResponse(json.dumps(data), 
        content_type="application/json")

@session_comet
def manage_logout(request):
    # need to do this before flushing the session because the session
    # key will change after the flush!
    
    # first delete the CometSessionIndex
    try:
        csi = CometSessionIndex.objects.get(session_key=\
            request.session.session_key)
        csi.delete()
    except CometSessionIndex.DoesNotExist:
        pass
    
    # also delete ALL the cometsessions associated with the request
    cs = CometSession.objects.filter(session_key=\
        request.session.session_key)
    for c in cs:
        c.delete()
    request.session.flush()
    return redirect(reverse('public_home'))

@session_comet
def manage_terms(request):
    return render(request, 'manage/terms.djhtml')
    
#### PARSE VIEWS

def manage_parse_invalid_link(request):
    """ Displays the invalid link template """
    return render(request, 'manage/parse-invalid-link.html')
    
@csrf_exempt
def manage_parse_frame(request):
    """ Required by Parse to use our urls insstead of theirs """
    return render(request, 'manage/parse-user-management.html')

@csrf_exempt
def manage_parse_password_reset(request):
    """ Displays the password reset template """
    return render(request, 'manage/parse-choose-password.html')
  
def manage_parse_password_reset_complete(request):
    """ Displays the password reset complete template """
    return render(request, 'manage/parse-password-updated.html')

