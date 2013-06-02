from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
import json, urllib

from forms import SettingsForm, SubscriptionForm
from libs.repunch import rputils

from parse.auth.decorators import login_required
from parse.apps.accounts.forms import SubscriptionForm as pSubscriptionForm, SettingsForm as pSettingsForm
from parse.apps.accounts import free, middle, heavy
from parse.apps.accounts.models import Settings

@login_required
def settings(request):
    data = {'settings_nav': True}
    account = request.session['account']
    settings = account.get_settings(); 
    if settings == None:
        settings = Settings.objects().create(Account=account.objectId,
                        retailer_id=rputils.generate_id())

    if request.method == 'POST':
        form = SettingsForm(request.POST) 
        pform = pSettingsForm(instance=settings, **request.POST.dict())
        if pform.is_valid(form.errors): 
            pform.update()
            data['success'] = "Settings have been saved."
        else:
            data['error'] = 'Error saving settings.';
    else:
        if settings == None:
            form = SettingsForm();
        else:
            form = SettingsForm(settings.__dict__);
    
    data['form'] = form
    data['settings'] = settings
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
            # consult accounts.__init__
            typeId = pform.subscription.get("SubscriptionType")
            if typeId == free.get('objectId'):
                pform.subscription.set("SubscriptionType", 
                                        middle.get('objectId'))
            elif typeId == middle.get('objectId'):
                pform.subscription.set("SubscriptionType", 
                                        heavy.get('objectId'))
            else:
                form.errors['level'] = "You cannot "+\
                                    "upgrade any further."                

            pform.update()
            account.subscription = pform.subscription
            account.subscription.store_cc(form.data['cc_number'],
                                            form.data['cc_cvv']);
            
            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Your account has been updated.'}))
    else:
        form = SubscriptionForm(subscription.__dict__)
    
    data['form'] = form
    return render(request, 'manage/account_upgrade.djhtml', data)
