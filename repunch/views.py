from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth import SESSION_KEY
import json

from parse.auth import login
from parse import session as SESSION
from apps.accounts.forms import LoginForm

""" Replaced with an ajax version for now.
def manage_login(request):
    data = {}
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid(): 
            if form.do_login(request):
                return redirect(reverse('store_index'))
            else:
                data['message'] = "Bad Login!"       
    else:
        form = LoginForm() # An unbound form

    
    data['form'] = form;
    return render(request, 'manage/login.djhtml', data)
"""

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
            c = login(request)
            c_type = type(c)
            if c_type is int:
                if c == 0:
                    data['code'] = 1 
                elif c == 1:
                    data['code'] = 2
            else:
                data['code'] = 3
        else:
            data['code'] =  0        
    else:
        data['form'] = LoginForm()
        # TODO ajax manage/login like the login dialog!
        return render(request, 'manage/login.djhtml', data)

    return HttpResponse(json.dumps(data), content_type="application/json")

def manage_logout(request):
    # need to clear the session
    request.session.flush()
    return redirect(reverse('public_home'))

def manage_terms(request):
    return render(request, 'manage/terms.djhtml')

