from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.forms.util import ErrorList
from django.contrib.auth import SESSION_KEY
from datetime import datetime
import json, urllib

from libs.dateutil.relativedelta import relativedelta
from repunch.settings import COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY
from apps import isdigit
from apps.accounts.forms import EmailForm, PasswordForm
from apps.stores.forms import SubscriptionForm
from parse import session as SESSION
from parse.comet import comet_receive
from parse.decorators import access_required, admin_only
from parse.auth.decorators import login_required, dev_login_required
from parse.apps.accounts import sub_type, UNLIMITED
from parse.apps.stores import IPOD, MONTHLY
from parse.apps.stores.models import Store, Subscription
from parse.utils import make_aware_to_utc
from parse.notifications import EMAIL_MONTHLY_SUBJECT,\
send_email_account_upgrade, send_email_receipt_monthly_success


@dev_login_required
@login_required
@access_required
def edit(request):
    account = request.session['account']
    store = SESSION.get_store(request.session)
    email_form, pass_form, data = None, None, {}

    if request.method == "POST":
        action, success = request.POST['action'], None
        if action == "email":
            email_form = EmailForm(account, request.POST)
            if email_form.is_valid():
                success = "Successfully updated email."
                
                # Need to make sure that the account is the latest - 
                # User in dashboard then signs up for a mobile account
                # and then edits store details = bug!
                account.fetch_all(clear_first=True, with_cache=False)
                # update the account - email = username!
                postEmail = email_form.cleaned_data['email']
                if account.email != postEmail:
                    account.email = postEmail
                    account.username = postEmail
                    account.update()
                    
        elif action == "password":
            pass_form = PasswordForm(account, request.POST)
            if pass_form.is_valid():
                success = "Successfully updated password."
                account.set_password(pass_form.cleaned_data['new'])
                account.update(save_password=True)
                
        if success:
            data['success'] = success
            # notify other dashboards of these changes
            payload={
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedAccount":account.jsonify()
            }
            comet_receive(store.objectId, payload)
            request.session["account"] = account
           
    if not email_form:
        email_form = EmailForm(None)
        email_form.initial = request.session['account'].__dict__.copy()
    if not pass_form:
        pass_form = PasswordForm(None)
        
    data["email_form"] = email_form
    data["password_form"] = pass_form
    
    return render(request, 'manage/account_edit.html', data)

@dev_login_required
@login_required
@admin_only(reverse_url="store_index")
def update_subscription(request):
    """
    This view is also used for explicit upgrades.
    """
    do_upgrade = request.GET.get("do_upgrade") is not None
    
    if do_upgrade:
        data = {'account_nav': True, 'upgrade':True}
    else:
        data = {'account_nav': True, 'update':True}
             
    store = SESSION.get_store(request.session)
    subscription = SESSION.get_subscription(request.session)
    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        form.subscription = subscription # to validate cc_number
        all_forms_valid = form.is_valid()
        
        if all_forms_valid:      
            # upgrade account if date_passed_user_limit is on
            # should fetch the most up-to-date subscription first
            subscription = Subscription.objects().get(objectId=\
                subscription.objectId)
            upgraded = False
            if subscription.date_passed_user_limit or do_upgrade:
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
                    
                    
            def invalid_card():
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
                        'manage/subscription_update.djhtml', data)
                    
            res = True
            # only store_cc if it is a digit (new)
            if str(form.data['cc_number']).isdigit():
                res = subscription.store_cc(form.data['cc_number'],
                                        form.data['cc_cvv'], False)
            if not res:
                return invalid_card()
            
            # if monthly billing failed
            if subscription.date_charge_failed:
                sub_cost = sub_type[subscription.get(\
                            "subscriptionType")]["monthly_cost"]
                invoice = subscription.charge_cc(\
                        sub_cost, EMAIL_MONTHLY_SUBJECT, MONTHLY)
                if invoice:
                    subscription.date_last_billed =\
                        subscription.date_last_billed +\
                        relativedelta(days=30)
                    subscription.date_charge_failed = None
                    subscription.update()
                    send_email_receipt_monthly_success(\
                        request.session['account'], 
                        store, subscription, invoice) 
                else:
                    return invalid_card()
            ###########
                        
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
            
            # Important that this is last since invalid_card may be
            # returned!
            subscription.update()
            
            # update the session cache
            request.session['store'] = store
            request.session['subscription'] = subscription
            
            # notify other dashboards of these changes
            payload={
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedSubscription":subscription.jsonify()
            }
            comet_receive(store.objectId, payload)
            
            # if coming from the message edit limit reached
            if do_upgrade:
                if request.session.get('from_limit_reached') and\
                    request.session.get('message_b4_upgrade'):
                    # redirect back to message_edit view to process 
                    return redirect(reverse('message_edit', 
                            args=(0,)) + "?%s" %\
                            urllib.urlencode({'send_message': '1'}))
            
            if do_upgrade:
                return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Your subscription has been upgraded.'}))
            else:
                return redirect(reverse('store_index')+ "?%s" %\
                            urllib.urlencode({'success':\
                                'Your subscription has been updated.'}))
    else:
        form = SubscriptionForm()
        form.initial = subscription.__dict__.copy()
        # add some asterisk to cc_number
        if form.initial.get("cc_number"):
            form.initial['cc_number'] = "*" * 12 +\
                form.initial.get('cc_number')[-4:]
                
        if do_upgrade:    
            from_limit_reached =\
                request.session.get("from_limit_reached")
            if from_limit_reached:
                data['from_limit_reached'] = from_limit_reached
            
    # update the session cache
    request.session['store'] = store
    request.session['subscription'] = subscription
    
    data['form'] = form
    return render(request, 'manage/subscription_update.djhtml', data)
