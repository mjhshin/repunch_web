from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
import json, urllib

from forms import SettingsForm, SubscriptionForm
from libs.repunch import rputils

from parse.auth.decorators import login_required
from parse.apps.accounts.forms import SubscriptionForm as pSubscriptionForm

@login_required
def settings(request):
    data = {'settings_nav': True}
    account = request.session['account']
    settings = account.get_settings(); 
    
    if request.method == 'POST': # If the form has been submitted...
        form = SettingsForm(request.POST, instance=settings) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            settings = form.save(commit=False)
            
            if settings.account_id == None:
                settings.account = account
                settings.retailer_id = rputils.generate_id()
            
            settings.save()
            
            data['success'] = "Settings have been saved."
        else:
            data['error'] = 'Error saving settings.';
    else:
        if settings == None:
            form = SettingsForm();
        else:
            form = SettingsForm(instance=settings);
    
    data['form'] = form
    return render(request, 'manage/settings.djhtml', data)


def refresh(request):
    if request.user.is_authenticated():
        data = {'success': False}
        account = request.session['account']
        settings = account.get_settings();
        if settings == None:
            raise Http404
        else:
            settings.retailer_id = rputils.generate_id()
            settings.save()
            
            data['success'] = True
            data['retailer_id'] = settings.retailer_id
        
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")
    
@login_required
def upgrade(request):
    data = {'account_nav': True}
    account = request.session['account']
    subscription = account.get('subscription')
    
    if request.method == 'POST': # If the form has been submitted...
        form = SubscriptionForm(request.POST) 
        pform = pSubscriptionForm(instance=subscription, 
                                    **request.POST.dict())

        if pform.is_valid(form.errors): 
            pform.subscription.SubscriptionType =\
                            subscription.SubscriptionType
            pform.update()
            account.subscription = pform.subscription
            account.subscription.store_cc(form.data['cc_number'],
                                            form.data['cc_cvv']);

            # TODO upgrade to next level
            
            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Your account has been updated.'}))
    else:
        form = SubscriptionForm(subscription.__dict__)
    
    data['form'] = form
    return render(request, 'manage/account_upgrade.djhtml', data)
