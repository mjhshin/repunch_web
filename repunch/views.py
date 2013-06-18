from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib.auth import SESSION_KEY
import pytz

from parse import session as SESSION
from apps.accounts.forms import LoginForm
from libs.repunch import rputils

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

def manage_logout(request):
    # need to clear the session
    request.session.flush()
    return redirect(reverse('public_home'))

def manage_terms(request):
    return render(request, 'manage/terms.djhtml')

