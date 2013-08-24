from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.forms.util import ErrorList
from django.contrib.auth import SESSION_KEY
from datetime import datetime
import json, urllib

from apps.accounts.models import AccountActivate
from repunch.settings import PHONE_COST_UNIT_COST,\
COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY
from apps.stores.forms import SettingsForm, SubscriptionForm,\
SubscriptionForm3
from parse import session as SESSION
from parse.comet import comet_receive
from parse.auth.decorators import login_required
from parse.apps.accounts import sub_type, UNLIMITED
from parse.apps.stores import SMARTPHONE
from parse.apps.stores.models import Settings, Store, Subscription
from parse.utils import make_aware_to_utc
from parse.notifications import send_email_receipt_smartphone,\
send_email_account_upgrade

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
def deactivate(request):
    """
    This does not delete anything! It merely sets the store's active
    field to false and logs the user out.
    """
    store = request.session['store']
    store.active = False
    store.update()
    return redirect(reverse('manage_logout'))

@login_required
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
            
            # notify other dashboards of this changes
            payload = {
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedSettings_one":settings.jsonify(),
                "updatedPunchesFacebook_int":\
                    store.punches_facebook,
            }
            comet_receive(store.objectId, payload)

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
            
            # notify other dashboards of these changes
            store = SESSION.get_store(request.session)
            payload = {
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedSettings_one":settings.jsonify()
            }
            comet_receive(store.objectId, payload)
            
            data['success'] = True
            data['retailer_pin'] = settings.retailer_pin
        
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")

@login_required
def update(request):
    data = {'account_nav': True, 'update':True}
    store = SESSION.get_store(request.session)
    subscription = SESSION.get_subscription(request.session)
    sub_orig = subscription.__dict__.copy()
    
    if request.method == 'POST':
        form = SubscriptionForm3(request.POST)
        form.subscription = subscription # to validate cc_number
        if form.is_valid():       
            # upgrade account if date_passed_user_limit is on
            # should fetch the most up-to-date subscription first
            subscription = Subscription.objects().get(objectId=\
                subscription.objectId)
            upgraded = False
            if subscription.date_passed_user_limit:
                level = subscription.get("subscriptionType")
                if level == 0:
                    subscription.set("subscriptionType", 1)
                    subscription.date_passed_user_limit = None
                    upgraded = True
                elif level == 1:
                    subscription.date_passed_user_limit = None
                    subscription.set("subscriptionType", 2) 
                    upgraded = True
                
            # subscription.update() called in store_cc
            subscription.update_locally(request.POST.dict(), False)
            
            d = datetime(int(request.POST['date_cc_expiration_year']),
                    int(request.POST['date_cc_expiration_month']), 1)
            subscription.set("date_cc_expiration", 
                make_aware_to_utc(d,
                    SESSION.get_store_timezone(request.session)) )
                    
            res = True
            # only store_cc if it is a digit
            if str(form.data['cc_number']).isdigit():
                res = subscription.store_cc(form.data['cc_number'],
                                            form.data['cc_cvv'])
            else:
                subscription.update()
            
            def invalid_card():
                # undo changes to subscription!
                sub = Subscription(**sub_orig)
                sub.update()
                
                # add some asterisk to cc_number
                if form.initial.get("cc_number"):
                    form.initial['cc_number'] = "*" * 12 +\
                        form.initial.get('cc_number')[-4:]
                errs = form._errors.setdefault(\
                    "cc_number", ErrorList())
                errs.append("Invalid credit " +\
                    "card. Please make sure that you provide " +\
                    "correct credit card information and that you " +\
                    "have sufficient funds, then try again.")
                data['form'] = form
                return render(request, 
                        'manage/account_upgrade.djhtml', data)
                            
            if not res:
                return invalid_card()
                        
            if request.POST.get("place_order") and\
                request.POST.get("place_order_amount").isdigit() and\
                int(request.POST.get("place_order_amount")) > 0:
                amount = int(request.POST.get("place_order_amount"))
                account = request.session['account']
                invoice = subscription.charge_cc(\
                    PHONE_COST_UNIT_COST*amount,
                    "Order placed for " +\
                    str(amount) + " phones", SMARTPHONE)
                if invoice:
                    send_email_receipt_smartphone(account, 
                        subscription, invoice, amount) 
                else:
                    return invalid_card()
                        
            if upgraded:  
                max_users = sub_type[\
                        subscription.subscriptionType]["max_users"]
                if max_users == UNLIMITED:
                    max_users = "Unlimited"
                package = {
                    "sub_type": sub_type[\
                        subscription.subscriptionType-1]["name"],
                    "new_sub_type": sub_type[\
                        subscription.subscriptionType]["name"],
                    "new_sub_type_cost": sub_type[\
                        subscription.subscriptionType]["monthly_cost"],
                    "new_max_patronStore_count": max_users, 
                }
                send_email_account_upgrade(request.session['account'],
                    store, package)
            
            # update the session cache
            request.session['store'] = store
            request.session['subscription'] = subscription
            
            # notify other dashboards of these changes
            payload={
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedSubscription_one":subscription.jsonify()
            }
            comet_receive(store.objectId, payload)
            
            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Your account has been updated.'}))
    else:
        form = SubscriptionForm3()
        form.initial = subscription.__dict__.copy()
        # add some asterisk to cc_number
        if form.initial.get("cc_number"):
            form.initial['cc_number'] = "*" * 12 +\
                form.initial.get('cc_number')[-4:]
            
    # update the session cache
    request.session['store'] = store
    request.session['subscription'] = subscription
    
    data['form'] = form
    return render(request, 'manage/account_upgrade.djhtml', data)

@login_required
def upgrade(request):
    """ 
    same as update except this also handles redirects from message
    """
    data = {'account_nav': True, 'upgrade':True}
    store = SESSION.get_store(request.session)
    subscription = SESSION.get_subscription(request.session)
    sub_orig = subscription.__dict__.copy()
    
    if request.method == 'POST':
        form = SubscriptionForm3(request.POST)
        form.subscription = subscription # to validate cc_number
        if form.is_valid(): 
            # should fetch the most up-to-date subscription first
            subscription = Subscription.objects().get(objectId=\
                subscription.objectId)
            upgraded = False
            level = subscription.get("subscriptionType")
            if level == 0:
                subscription.set("subscriptionType", 1)
                subscription.date_passed_user_limit = None
                upgraded = True
            elif level == 1:
                subscription.set("subscriptionType", 2)  
                subscription.date_passed_user_limit = None
                upgraded = True 

            # subscription.update() called in store_cc
            subscription.update_locally(request.POST.dict(), False)
            
            d = datetime(int(request.POST['date_cc_expiration_year']),
                    int(request.POST['date_cc_expiration_month']), 1)
            subscription.set("date_cc_expiration", 
                make_aware_to_utc(d,
                    SESSION.get_store_timezone(request.session)) )
                    
            res = True
            # only store_cc if it is a digit
            if str(form.data['cc_number']).isdigit():
                res = subscription.store_cc(form.data['cc_number'],
                                            form.data['cc_cvv'])
            else:
                subscription.update()
                    
            def invalid_card():
                # undo changes to subscription!
                sub = Subscription(**sub_orig)
                sub.update()
                
                # add some asterisk to cc_number
                if form.initial.get("cc_number"):
                    form.initial['cc_number'] = "*" * 12 +\
                        form.initial.get('cc_number')[-4:]
                errs = form._errors.setdefault(\
                    "cc_number", ErrorList())
                errs.append("Invalid credit " +\
                    "card. Please make sure that you provide " +\
                    "correct credit card information and that you " +\
                    "have sufficient funds, then try again.")
                data['form'] = form
                from_limit_reached =\
                    request.session.get("from_limit_reached")
                if from_limit_reached:
                    data['from_limit_reached'] = from_limit_reached
                return render(request, 
                        'manage/account_upgrade.djhtml', data)
                    
            if not res:
                return invalid_card()
                        
            if request.POST.get("place_order") and\
                request.POST.get("place_order_amount").isdigit() and\
                int(request.POST.get("place_order_amount")) > 0:
                amount = int(request.POST.get("place_order_amount"))
                account = request.session['account']
                invoice = subscription.charge_cc(\
                    PHONE_COST_UNIT_COST*amount,
                    "Order placed for " +\
                    str(amount) + " phones", SMARTPHONE)
                if invoice:
                    send_email_receipt_smartphone(account, 
                        subscription, invoice, amount)
                else:
                    return invalid_card()
                        
            if upgraded:  
                max_users = sub_type[\
                        subscription.subscriptionType]["max_users"]
                if max_users == UNLIMITED:
                    max_users = "Unlimited"
                package = {
                    "sub_type": sub_type[\
                        subscription.subscriptionType-1]["name"],
                    "new_sub_type": sub_type[\
                        subscription.subscriptionType]["name"],
                    "new_sub_type_cost": sub_type[\
                        subscription.subscriptionType]["monthly_cost"],
                    "new_max_patronStore_count": max_users, 
                }
                send_email_account_upgrade(request.session['account'],
                    store, package)
                    
            # update the session cache
            request.session['store'] = store
            request.session['subscription'] = subscription
            
            # notify other dashboards of these changes
            payload={
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedSubscription_one":subscription.jsonify()
            }
            comet_receive(store.objectId, payload)
            
            # if coming from the message edit limit reached
            if request.session.get('from_limit_reached') and\
                request.session.get('message_b4_upgrade'):
                # redirect back to message_edit view to process the 
                return redirect(reverse('message_edit', 
                        args=(0,)) + "?%s" %\
                        urllib.urlencode({'send_message': '1'}))

            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Your account has been updated.'}))
    else:
        form = SubscriptionForm3()
        form.initial = subscription.__dict__.copy()
        # add some asterisk to cc_number
        if form.initial.get("cc_number"):
            form.initial['cc_number'] = "*" * 12 +\
                form.initial.get('cc_number')[-4:]
            
        from_limit_reached = request.session.get("from_limit_reached")
        if from_limit_reached:
            data['from_limit_reached'] = from_limit_reached
            
    # update the session cache
    request.session['store'] = store
    request.session['subscription'] = subscription
    
    data['form'] = form
    return render(request, 'manage/account_upgrade.djhtml', data)
