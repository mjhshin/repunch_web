from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core import mail 
from datetime import datetime
import json, pytz

from forms import ContactForm
from repunch.settings import PHONE_COST_UNIT_COST, DEBUG
from parse.decorators import session_comet
from parse.auth.utils import request_password_reset
from parse.notifications import send_email_signup, send_email_receipt
from apps.db_static.models import Category
from apps.accounts.forms import AccountForm
from parse.apps.stores import format_phone_number
from apps.stores.forms import StoreSignUpForm, SubscriptionForm2
from libs.repunch import rputils

from parse.auth import login
from parse.utils import make_aware_to_utc
from parse.apps.accounts.models import Account
from parse.apps.accounts import sub_type, UNLIMITED
from parse.apps.stores.models import Store, Subscription,\
Settings

@session_comet
def index(request):
    if request.session.get('account') is not None and\
        request.session.get('store') is not None and\
        request.session.get('subscription') is not None:
        return redirect(reverse('store_index'))
        
    data = {'home_nav': True}
    return render(request, 'public/index.djhtml', data)

@session_comet
def learn(request):
    data = {'learn_nav': True}
    
    data['unlimited'] = UNLIMITED
    types = [value for value in sub_type.itervalues()]
    data['types'] = types
    return render(request, 'public/learn.djhtml', data)

@session_comet
def faq(request):
    data = {'faq_nav': True}
    data['form'] = ContactForm() # An unbound form
    return render(request, 'public/faq.djhtml', data)

@session_comet
def about(request):
    data = {'about_nav': True}
    return render(request, 'public/about.djhtml', data)

@session_comet 
def terms(request):
    return render(request, 'public/terms.djhtml')

@session_comet
def privacy(request):
    return render(request, 'public/privacy.djhtml')

@session_comet
def contact(request):
    if request.method == 'POST': 
        form = ContactForm(request.POST) 
        if form.is_valid(): 
            form.send()
            return redirect(reverse('public_thank_you'))
    else:
        form = ContactForm()

    return render(request, 'public/contact.djhtml', {'form': form, })

@session_comet
def thank_you(request):
    return render(request, 'public/thank_you.djhtml')

@session_comet
def jobs(request):
    return render(request, 'public/jobs.djhtml')

def categories(request):
    """ takes in ajax requests and returns a list of choices for
    autocompletion in json format """
    # term is the key in request.GET
    if request.method == "GET" or request.is_ajax():
        categories = Category.objects.filter(name__istartswith=\
                        request.GET['term'].strip())[:8]
                        
        data = []
        for cat in categories:
            data.append(cat.name)

        return HttpResponse(json.dumps(data), 
                    content_type="application/json")
    else:
        return HttpResponse('')
        
def password_reset(request):
    """
    Calls Parse's requestPasswordReset
    """
    return HttpResponse(json.dumps({"res":\
        request_password_reset(request.POST['forgot-pass-email'])}), 
        content_type="application/json")
        
@session_comet
def sign_up2(request):
    """
    Second part of the signup process.
    """
    data = {'sign_up_nav': True}
    
    if request.method == 'POST' or request.is_ajax():
        # some keys are (were) repeated so must catch this at init
        subscription_form = SubscriptionForm2(request.POST)
        
        if subscription_form.is_valid() and\
            request.session['store-tmp'] and\
            request.session['settings-tmp'] and\
            request.session['account-tmp']:
            
            postDict = request.POST.dict()
            
            store = request.session['store-tmp']
            settings = request.session['settings-tmp']
            account = request.session['account-tmp']

            # create subscription
            subscription = Subscription(**postDict)
            tz = pytz.timezone(store.store_timezone)
            exp = make_aware_to_utc(datetime(\
                int(postDict['date_cc_expiration_year']),
                int(postDict['date_cc_expiration_month']), 1), tz)
            subscription.set("date_cc_expiration", exp)
            subscription.subscriptionType = 0
            # make sure to use the correct POST info
            subscription.first_name = request.POST['first_name2']
            subscription.last_name  = request.POST['last_name2']
            subscription.city = request.POST['city2']
            subscription.state = request.POST['state2']
            subscription.zip = request.POST['zip2']
            subscription.country = request.POST['country2']
            subscription.create()

            # create store
            store.Subscription = subscription.objectId
            
            # finally create everything
            settings.create()
            store.Settings = settings.objectId
            store.create()
            settings.Store = store.objectId
            settings.update()
            account.Store = store.objectId
            account.create()
            
            # set the subscription's store (uppdate called in store_cc
            subscription.Store = store.objectId
            subscription.store_cc(subscription_form.data['cc_number'],
                            subscription_form.data['cc_cvv'])
            
            # need to put username and pass in request
            requestDict = request.POST.dict().copy()
            requestDict['username'] = account.username
            requestDict['password'] = account.password
            
            ####
            conn = mail.get_connection(fail_silently=(not DEBUG))
            
            if request.POST.get("place_order") and\
                request.POST.get("place_order_amount").isdigit():
                amount = int(request.POST.get("place_order_amount"))
                if amount > 0:
                    invoice = subscription.charge_cc(\
                        PHONE_COST_UNIT_COST*amount,
                        "Order placed for " +\
                        str(amount) + " phones", "smartphone")
                    send_email_receipt(account, invoice, amount)
            
            # send matt and new user a pretty email.
            send_email_signup(account)
            
            conn.close()

            # auto login
            user_login = login(request, requestDict)
            if user_login != None:
                data = {"code":-1}
                # -1 - invalid request
                # 0 - invalid form input
                # 1 - bad login credentials
                # 2 - subscription is not active
                # 3 - success (login now)
                # 4 - go to part 2
                if type(user_login) is int: # subscription not active
                    data['code'] = 2
                else:
                    # required for datetime awareness!
                    rputils.set_timezone(request, tz)
                    data['code'] = 3
                return HttpResponse(json.dumps(data), 
                            content_type="application/json")
            else:
                # should never go here 
                pass
    elif not (request.session['store-tmp'] and\
            request.session['settings-tmp'] and\
            request.session['account-tmp']):
        return render(request, 'public/signup.djhtml', data)
    else:
        subscription_form = SubscriptionForm2()

    data['store_form'] = StoreSignUpForm(\
        request.session['store-tmp'].__dict__.copy())
    data['subscription_form'] = subscription_form
    return render(request, 'public/signup2.djhtml', data)

@session_comet  
def sign_up(request):
    """ 
    renders the signup page on GET and returns a json object on POST.
    """
    data = {'sign_up_nav': True}
    
    if request.method == 'POST' or request.is_ajax():
        # some keys are repeated so must catch this at init
        store_form = StoreSignUpForm(request.POST)
        account_form = AccountForm(request.POST)
        
        if store_form.is_valid() and account_form.is_valid():
            postDict = request.POST.dict()

            # create store
            tz = rputils.get_timezone(request.POST.get(\
                    "store_timezone"))
            store = Store(**postDict)
            store.store_timezone = tz.zone
            # set defaults for these guys to prevent 
            # ParseObjects from making parse calls repeatedly
            store.punches_facebook = 0
            # format the phone number
            store.phone_number =\
                format_phone_number(request.POST['phone_number'])
            store.set("store_description", "The " + store.store_name)
            store.set("hours", [])
            store.set("rewards", [])
            store.set("categories", [])
            names = request.POST.get("categories")
            if names:
                for name in names.split(",")[:-1]:
                    alias = Category.objects.filter(name__iexact=\
                                                    name)
                    if len(alias) > 0:
                        alias = alias[0].alias
                        store.categories.append({
                            "alias":alias,
                            "name":name })
            # coordinates
            # the call to get map data is actually also in the clean 
            full_address = " ".join(\
                store.get_full_address().split(", "))
            map_data = rputils.get_map_data(full_address)
            store.set("coordinates", map_data.get("coordinates"))
            store.set("neighborhood", 
                store.get_best_fit_neighborhood(\
                    map_data.get("neighborhood")))
            
            # create settings
            settings = Settings(retailer_pin=\
                        Settings.generate_id(),
                        punches_employee=5, Store=store.objectId)
            store.set('settings', settings)

            # create account
            account = Account(**postDict)
            account.account_type = "store"
            account.set_password(request.POST.get('password'))
            account.set("store", store)
            
            # Create and save store up to Parse (do in part 2)
            # store.create()
            request.session['store-tmp'] = store
            request.session['settings-tmp'] = settings
            request.session['account-tmp'] = account
            
            # -1 - invalid request
            # 0 - invalid form input
            # 1 - bad login credentials
            # 2 - subscription is not active
            # 3 - success (login now)
            # 4 - go to part 2
            return HttpResponse(json.dumps({"code":4}), 
                            content_type="application/json")
           
    else:
        store_form = StoreSignUpForm()
        account_form = AccountForm()
        
    data['store_form'] = store_form
    data['account_form'] = account_form
    return render(request, 'public/signup.djhtml', data)

