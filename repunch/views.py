from django.shortcuts import redirect, render
from django.db import IntegrityError
from django.contrib.sessions.backends.cache import SessionStore
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import authenticate
import json, thread

from parse import session as SESSION
from parse.auth import login, logout
from parse.auth.decorators import dev_login_required
from apps.accounts.forms import LoginForm
from apps.comet.models import CometSessionIndex
from repunch.settings import PRODUCTION_SERVER, DEVELOPMENT_TOKEN,\
RECAPTCHA_TOKEN, RECAPTCHA_ATTEMPTS

def manage_dev_login(request):
    """
    Used for the development site
    """
    # just redirect user to home page if they already logged in
    # redirect user to home page if accessed from the production site
    if request.session.get(DEVELOPMENT_TOKEN) or PRODUCTION_SERVER:
        return redirect(reverse("public_home"))
        
    if request.method == "POST":
        if authenticate(username=request.POST['username'],
            password=request.POST['password']) is not None:
            # just insert an arbitrary object
            request.session[DEVELOPMENT_TOKEN] = 1
            request.session.set_expiry(0)
            return HttpResponse(json.dumps({"code":1}), 
                content_type="application/json")
        else:
            return HttpResponse(json.dumps({"code":0}), 
                content_type="application/json")
    else:
        return render(request, 'manage/dev_login.djhtml', {})

@dev_login_required
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
        4 - employee with no access
        5 - employee pending
        6 - invalid recaptcha response
    """
    data = {"code":-1}
    if request.method == 'POST' or request.is_ajax():
        form = LoginForm(request.POST)
        if form.is_valid(): 
            c = login(request, request.POST.dict().copy())
            c_type = type(c)
            if c_type is int:
                if c == 0: # bad login credentials
                    data['code'] = 1 
                elif c == 1:
                    data['code'] = 2
                elif c == 2:
                    data['code'] = 4
                elif c == 3:
                    data['code'] = 5
                elif c == 4: # recaptcha response fail
                    data['code'] = 6
            else:
                data['code'] = 3
                        
                # manually check the next parameter
                next = request.GET.get("next")
                if not next:
                    next = reverse("store_index")
                data['redirect_url'] = next
                # user may try to login on another tab when already in
                try:
                    CometSessionIndex.objects.create(session_key=\
                        request.session.session_key, 
                        store_id=request.session['store'].objectId,
                        last_updated=timezone.now())
                except IntegrityError:
                    pass
                            
        else:
            data['code'] =  0        
    else:
        if request.session.get('account'):
            return redirect(reverse('store_index'))
        data['form'] = LoginForm()
        return render(request, 'manage/login.djhtml', data)
        
    if data['code'] in (1, 6):
        data['display_recaptcha'] =\
            RECAPTCHA_TOKEN in request.session and request.session[\
            RECAPTCHA_TOKEN] >= RECAPTCHA_ATTEMPTS

    return HttpResponse(json.dumps(data), 
        content_type="application/json")

def manage_logout(request):
    # need to do this before flushing the session because the session
    # key will change after the flush!
    return logout(request, 'public_home')

@dev_login_required
def manage_terms(request):
    return render(request, 'manage/terms.djhtml')
    
#### PARSE VIEWS

@dev_login_required
def manage_parse_invalid_link(request):
    """ Displays the invalid link template """
    return render(request, 'manage/parse-invalid-link.html')
    
@dev_login_required
@csrf_exempt
def manage_parse_frame(request):
    """ Required by Parse to use our urls insstead of theirs """
    return render(request, 'manage/parse-user-management.html')

@dev_login_required
@csrf_exempt
def manage_parse_password_reset(request):
    """ Displays the password reset template """
    return render(request, 'manage/parse-choose-password.html')
  
@dev_login_required
def manage_parse_password_reset_complete(request):
    """ Displays the password reset complete template """
    return render(request, 'manage/parse-password-updated.html')

