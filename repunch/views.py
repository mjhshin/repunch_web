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
from parse.apps.accounts.models import Account
from parse.utils import cloud_call
from parse.comet import comet_receive
from parse.auth import login, logout
from parse.auth.decorators import dev_login_required
from apps.accounts.forms import LoginForm
from apps.comet.models import CometSessionIndex
from repunch.settings import PRODUCTION_SERVER, DEVELOPMENT_TOKEN,\
RECAPTCHA_TOKEN, RECAPTCHA_ATTEMPTS, CLOUD_LOGGER_TRIGGER_KEY,\
ADMIN_CONTROL_KEY, COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY

def manage_admin_controls(request):
    """
    To turn on god_mode:
    ...repunch.com/manage/admin-controls?action=god_mode&flag=1&
    email=abc@email.com&key=9p8437wk34z5ymurukdp9w34px7iuhsruhio
    """
    
    if request.method == "GET":
        params = request.GET.dict()
        key = params.get("key")
        action = params.get("action")
        
        if key == ADMIN_CONTROL_KEY:
            if action == "god_mode":
                flag = params.get("flag")
                email = params.get("email", "")
                acc = Account.objects().get(email=email, Store__ne=None,
                    include="Store.Subscription")
                if not acc:
                    return HttpResponse("User with email %s not found." %\
                        (email,))
                
                sub = acc.store.subscription
                sub.god_mode = flag != "0"
                sub.update()
                
                payload = {
                    COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                    "updatedSubscription": sub.jsonify(),
                }
                comet_receive(acc.store.objectId, payload)
                
                # go out with the latest session in case this user is
                # the one that triggered this action
                request.session.clear()                           
                request.session.update(SessionStore(request.session.session_key))
                
                if sub.god_mode:
                    on_off = "on"
                else:
                    on_off = "off"
                
                return HttpResponse("Successfully turned god mode "+\
                    "%s for user with email %s" % (on_off, email))
                
            else:
                return HttpResponse("Invalid action: %s" % (action,))
        
        else:
            return HttpResponse("Wrong key: %s" % (key,))
    
    return HttpResponse("Bad Request")
    

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
    if request.method == 'POST':
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
    
def manage_cloud_trigger(request):
    """
    Simply calls the trigger_cloud_logger cloud code.
    """
    if request.method == "GET":
        key = request.GET.get("key")
        if key == CLOUD_LOGGER_TRIGGER_KEY:
            cloud_call("trigger_cloud_logger", {
                "extra_message":\
                    request.GET.get("extra_message", "Still running")
            })
            return HttpResponse("<p>Successfully called "+\
                "trigger_cloud_logger.</p><p>Please wait at most"+\
                " 40 seconds to receive the notification in your email.</p>")
    
    return HttpResponse("Bad Request")
