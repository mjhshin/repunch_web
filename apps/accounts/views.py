from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.contrib.auth import SESSION_KEY
import json, urllib

from apps.stores.forms import SettingsForm, SubscriptionForm
from libs.repunch import rputils

from parse.auth.decorators import login_required
from parse.apps.stores.models import Settings

@login_required
def settings(request):
    data = {'settings_nav': True}
    account = request.session['account']
    store = account.get('store')
    settings = store.get('settings')

    # settings should never be none but just in case
    if settings == None:
        settings = Settings.objects().create(retailer_pin=rputils.generate_id())
        store.Settings = settings.objectId
        store.settings = settings
        store.update()
        account.store = store
        request.session['account'] = account

    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid(): 
            settings.update_locally(request.POST.dict(), False)
            settings.update()
            # Shin chose to move punches_facebook to Store...
            store.set("punches_facebook", 
                        request.POST["punches_facebook"])
            store.Settings = settings.objectId
            store.settings = settings
            store.update()
            account.store = store
            request.session['account'] = account

            data['success'] = "Settings have been saved."
        else:
            data['error'] = 'Error saving settings.';
    else:
        form = SettingsForm(settings.__dict__);
        # shin chose to move punches_facebook to Store...
        form.data['punches_facebook'] = store.get('punches_facebook')
    
    data['form'] = form
    data['settings'] = settings
    return render(request, 'manage/settings.djhtml', data)


def refresh(request):
    if request.session.get('account') and\
            request.session.get(SESSION_KEY):
        data = {'success': False}
        account = request.session['account']
        store = account.get('store')
        settings = store.get('settings');
        
        if settings == None:
            raise Http404
        else:
            settings.set('retailer_pin', rputils.generate_id())
            settings.update()
            store.settings = settings
            account.store = store
            request.session['account'] = account
            
            data['success'] = True
            data['retailer_pin'] = settings.retailer_pin
        
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")

@login_required
def update(request):
    data = {'account_nav': True}
    # I think that a copy is made here so any changes made to account
    # will not affect the account object in the session. maybe
    account = request.session['account']
    subscription = account.get("store").get('subscription')
    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST) 

        if form.is_valid():       
            # subscription.update() called in store_cc
            subscription.update_locally(request.POST.dict(), False)
            
            try:
                subscription.store_cc(form.data['cc_number'],
                                            form.data['cc_cvv']);
            except Exception as e:
                form = SubscriptionForm(subscription.__dict__)
                form.errors['__all__'] =\
                    form.error_class([e])
                data['form'] = form
                return render(request, 
                        'manage/account_upgrade.djhtml', data)

            # just in case account is a copy as noted above
            account.store.subscription = subscription
            request.session['account'] = account

            

            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Your account has been updated.'}))
    else:
        form = SubscriptionForm(subscription.__dict__)
    
    data['form'] = form
    return render(request, 'manage/account_upgrade.djhtml', data)

@login_required
def upgrade(request):
    """ same as update expect this upgrades the subscriptionType """
    data = {'account_nav': True}
    # I think that a copy is made here so any changes made to account
    # will not affect the account object in the session. maybe
    account = request.session['account']
    subscription = account.get("store").get('subscription')
    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST) 

        if form.is_valid(): 
            # consult accounts.__init__
            level = subscription.get("subscriptionType")
            if level == 0:
                subscription.set("subscriptionType", 1)
            elif level == 1:
                subscription.set("subscriptionType", 2)        

            # subscription.update() called in store_cc
            subscription.update_locally(request.POST.dict(), False)
            

            try:
                subscription.store_cc(form.data['cc_number'],
                                            form.data['cc_cvv']);
            except Exception as e:
                form = SubscriptionForm(subscription.__dict__)
                form.errors['__all__'] =\
                    form.error_class([e])
                data['form'] = form
                return render(request, 
                        'manage/account_upgrade.djhtml', data)

            # just in case account is a copy as noted above
            account.store.subscription = subscription
            request.session['account'] = account

            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Your account has been updated.'}))
    else:
        form = SubscriptionForm(subscription.__dict__)
    
    data['form'] = form
    return render(request, 'manage/account_upgrade.djhtml', data)
