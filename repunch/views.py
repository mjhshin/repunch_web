from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout
import pytz

from apps.accounts.forms import LoginForm
from libs.repunch import rputils

def manage_login(request):
    data = {}
    if request.method == 'POST': # If the form has been submitted...
        form = LoginForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            user = form.do_login(request)
            if(user is not None):
                login(request, user)
                return redirect(reverse('store_index'))
            else:
                data['message'] = "Bad Login!"       
    else:
        form = LoginForm() # An unbound form

    
    data['form'] = form;
    return render(request, 'manage/login.djhtml', data)


def manage_logout(request):
    request.session['account'] = None
    logout(request)
    return redirect(reverse('public_home'))

def manage_terms(request):
    return render(request, 'manage/terms.djhtml')

