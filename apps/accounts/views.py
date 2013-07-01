from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.contrib.auth import SESSION_KEY
from datetime import datetime
import json, urllib

from apps.accounts.models import AccountActivate
from repunch.settings import PHONE_COST_UNIT_COST
from apps.stores.forms import SettingsForm, SubscriptionForm,\
SubscriptionForm3
from parse.decorators import session_comet
from parse import session as SESSION
from parse.auth.decorators import login_required
from parse.apps.stores.models import Settings, Store

@csrf_exempt
def activate(request):
    """
    Handles account activation from email form sent at user sign up.
    """
    if request.method == "POST":
        store_id = request.POST['store_id']
        act_id = request.POST['act_id']
        act = AccountActivate.objects.filter(id=act_id,
                store_id=store_id)
        if len(act) > 0:
            act = act[0]
            if not act.is_used: # exist and unused!
                act.is_used = True
                act.save()
                store = Store.objects().get(objectId=store_id)
                if store:
                    store.active = True
                    store.update()
                    return HttpResponse(store.get(\
                        "store_name").capitalize() +\
                        " has been activated.")
                else:
                    return HttpResponse("Account/store not found.")    
            else: # used
                return HttpResponse("This form has already "+\
                    "been used.")                
    
    return HttpResponse("Bad request")

@login_required
@session_comet
def settings(request):
    data = {'settings_nav': True}
    store = SESSION.get_store(request.session)
    settings = SESSION.get_settings(request.session)
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid(): 
            # expect numbers so cast to int
            dct = request.POST.dict().copy()
            dct['punches_employee'] = int(dct['punches_employee'])
            settings.update_locally(dct, False)
            settings.update()
            # Shin chose to move punches_facebook to Store...
            store.set("punches_facebook", 
                        int(request.POST["punches_facebook"]))
            store.Settings = settings.objectId
            store.settings = settings
            store.update()

            data['success'] = "Settings have been saved."
        else:
            data['error'] = 'Error saving settings.';
    else:
        form = SettingsForm()
        form.initial = settings.__dict__.copy()
        # shin chose to move punches_facebook to Store...
        form.initial['punches_facebook'] =\
            store.get('punches_facebook')
    
    # update the session cache
    request.session['store'] = store
    request.session['settings'] = settings
    
    data['form'] = form
    data['settings'] = settings
    return render(request, 'manage/settings.djhtml', data)

@login_required
def refresh(request):
    if request.session.get('account') and\
            request.session.get(SESSION_KEY):
        data = {'success': False}
        settings = SESSION.get_settings(request.session)
        
        if settings == None:
            raise Http404
        else:
            settings.set('retailer_pin', Settings.generate_id())
            settings.update()
            
            # update the session cache
            request.session['settings'] = settings
            
            data['success'] = True
            data['retailer_pin'] = settings.retailer_pin
        
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")

@login_required
@session_comet
def update(request):
    data = {'account_nav': True, 'update':True}
    store = SESSION.get_store(request.session)
    subscription = SESSION.get_subscription(request.session)
    
    if request.method == 'POST':
        form = SubscriptionForm3(request.POST)
        form.subscription = subscription # to validate cc_number
        if form.is_valid():       
            # subscription.update() called in store_cc
            subscription.update_locally(request.POST.dict(), False)
            
            try:
                subscription.set("date_cc_expiration", 
                    datetime(int(request.POST['date_cc_expiration_year']),
                        int(request.POST['date_cc_expiration_month']), 1))
                subscription.store_cc(form.data['cc_number'],
                                            form.data['cc_cvv'])
            except Exception as e:
                form = SubscriptionForm(subscription.__dict__.copy())
                form.errors['__all__'] =\
                    form.error_class([e])
                data['form'] = form
                return render(request, 
                        'manage/account_upgrade.djhtml', data)
                        
            if request.POST.get("place_order") and\
                request.POST.get("place_order_amount").isdigit():
                amount = int(request.POST.get("place_order_amount"))
                account = request.session['account']
                invoice = subscription.charge_cc(\
                    PHONE_COST_UNIT_COST*amount,
                    "Order placed for " +\
                    str(amount) + " phones", "smartphone")
                if amount > 0:
                    send_email_receipt(account, invoice, amount) 
            
            # update the session cache
            request.session['store'] = store
            request.session['subscription'] = subscription
            
            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Your account has been updated.'}))
    else:
        form = SubscriptionForm3()
        form.initial = subscription.__dict__.copy()
        # add some asterisk to cc_number
        form.initial['cc_number'] = "*" * 12 +\
            form.initial.get('cc_number')[-4:]
            
    # update the session cache
    request.session['store'] = store
    request.session['subscription'] = subscription
    
    data['form'] = form
    return render(request, 'manage/account_upgrade.djhtml', data)

@login_required
@session_comet
def upgrade(request):
    """ same as update expect this upgrades the subscriptionType """
    data = {'account_nav': True, 'upgrade':True}
    store = SESSION.get_store(request.session)
    subscription = SESSION.get_subscription(request.session)
    
    if request.method == 'POST':
        form = SubscriptionForm3(request.POST)
        form.subscription = subscription # to validate cc_number
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
                subscription.set("date_cc_expiration", 
                datetime(int(request.POST['date_cc_expiration_year']),
                    int(request.POST['date_cc_expiration_month']), 1))
                subscription.store_cc(form.data['cc_number'],
                                            form.data['cc_cvv'])
            except Exception as e:
                form = SubscriptionForm(subscription.__dict__.copy())
                form.errors['__all__'] = form.error_class([e])
                data['form'] = form
                return render(request, 
                        'manage/account_upgrade.djhtml', data)
                        
            if request.POST.get("place_order") and\
                request.POST.get("place_order_amount").isdigit():
                amount = int(request.POST.get("place_order_amount"))
                account = request.session['account']
                invoice = subscription.charge_cc(\
                    PHONE_COST_UNIT_COST*amount,
                    "Order placed for " +\
                    str(amount) + " phones", "smartphone")
                if amount > 0:
                    send_email_receipt(account, invoice, amount)
                    
            # update the session cache
            request.session['store'] = store
            request.session['subscription'] = subscription

            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Your account has been updated.'}))
    else:
        form = SubscriptionForm3()
        form.initial = subscription.__dict__.copy()
        # add some asterisk to cc_number
        form.initial['cc_number'] = "*" * 12 +\
            form.initial.get('cc_number')[-4:]
            
    # update the session cache
    request.session['store'] = store
    request.session['subscription'] = subscription
    
    data['form'] = form
    return render(request, 'manage/account_upgrade.djhtml', data)
