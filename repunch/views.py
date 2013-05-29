from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib.auth import SESSION_KEY
import pytz

from parse.apps.accounts.forms import LoginForm as pLoginForm
from apps.accounts.forms import LoginForm
from libs.repunch import rputils

# TODO REPLACE DJANGO FORMS

def manage_login(request):
    data = {}
    if request.method == 'POST': # If the form has been submitted...
        form = LoginForm(request.POST) # A form bound to the POST data
        pform = pLoginForm(request.POST)
        if pform.is_valid(): # All validation rules pass
            user = pform.do_login(request)
            if user:
                return redirect(reverse('store_index'))
            else:
                data['message'] = "Bad Login!"       
    else:
        form = LoginForm() # An unbound form

    
    data['form'] = form;
    return render(request, 'manage/login.djhtml', data)

def manage_logout(request):
    request.session['account'] = None
    request.session[SESSION_KEY] = None
    return redirect(reverse('public_home'))

def manage_terms(request):
    return render(request, 'manage/terms.djhtml')

