from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from datetime import datetime
import json

from parse.notifications import send_email_signup
from parse.apps.accounts import order_placed, user_signup
from apps.db_static.models import Category
from apps.accounts.forms import AccountForm
from parse.apps.stores import format_phone_number
from apps.stores.forms import StoreSignUpForm, SubscriptionForm2
from forms import ContactForm
from libs.repunch import rputils

from parse.auth import login
from parse.apps.accounts.models import Account
from parse.apps.accounts import sub_type, UNLIMITED
from parse.apps.stores.models import Store, Subscription,\
Settings

def index(request):
    if request.session.get('account'):
        return redirect(reverse('store_index'))
        
    data = {'home_nav': True}
    return render(request, 'public/index.djhtml', data)

def learn(request):
    data = {'learn_nav': True}
    
    data['unlimited'] = UNLIMITED
    types = [value for value in sub_type.itervalues()]
    data['types'] = types
    return render(request, 'public/learn.djhtml', data)

def faq(request):
    data = {'faq_nav': True}
    data['form'] = ContactForm() # An unbound form
    return render(request, 'public/faq.djhtml', data)

def about(request):
    data = {'about_nav': True}
    return render(request, 'public/about.djhtml', data)
    
def terms(request):
    return render(request, 'public/terms.djhtml')

def privacy(request):
    return render(request, 'public/privacy.djhtml')

def contact(request):
    if request.method == 'POST': 
        form = ContactForm(request.POST) 
        if form.is_valid(): 
            form.send()
            return redirect(reverse('public_thank_you'))
    else:
        form = ContactForm()

    return render(request, 'public/contact.djhtml', {'form': form, })

def thank_you(request):
    return render(request, 'public/thank_you.djhtml')

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

def sign_up(request):
    """ 
    renders the signup page on GET and returns a json object on POST.
    """
    data = {'sign_up_nav': True}
    
    if request.method == 'POST' or request.is_ajax():
        # some keys are repeated so must catch this at init
        store_form = StoreSignUpForm(request.POST)
        account_form = AccountForm(request.POST)
        subscription_form = SubscriptionForm2(request.POST)
        
        if store_form.is_valid() and account_form.is_valid() and\
           subscription_form.is_valid():
            postDict = request.POST.dict()

            # create subscription
            subscription = Subscription(**postDict)
            subscription.set("date_cc_expiration", 
                datetime(int(postDict['cc_expiration_year']),
                    int(postDict['cc_expiration_month']), 1))
            subscription.subscriptionType = 0
            # make sure to use the correct POST info
            subscription.first_name = request.POST['first_name2']
            subscription.last_name  = request.POST['last_name2']
            subscription.city = request.POST['city2']
            subscription.state = request.POST['state2']
            subscription.zip = request.POST['zip2']
            subscription.country = request.POST['country2']
            subscription.create()
            subscription.store_cc(subscription_form.data['cc_number'],
                            subscription_form.data['cc_cvv'])

            # create store
            tz = rputils.get_timezone(request.POST.get(\
                    "store_timezone"))
            store = Store(**postDict)
            store.store_timezone = tz.zone
            store.Subscription = subscription.objectId
            # set defaults for these guys to prevent 
            # ParseObjects from making parse calls repeatedly
            store.punches_facebook = 0
            # format the phone number
            store.phone_number =\
                format_phone_number(request.POST['phone_number'])
            store.set("description", "The " + store.store_name)
            store.set("hours", [])
            store.set("rewards", [])
            # TODO get geopoint from google API call
            # also fill up cross streets and validate address
            # TODO html address auto complete?
            store.set("coordinates", [40.42, -73.59]) 
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
            store.create()    
            
            # create settings
            settings = Settings.objects().create(retailer_pin=\
                        rputils.generate_id(), punches_customer=1,
                        punches_employee=5, Store=store.objectId)
            store.Settings = settings.objectId
            store.set('settings', settings)
            store.update()

            # create account
            account = Account(**postDict)
            account.Store = store.objectId
            account.account_type = "store"
            account.set_password(request.POST.get('password'))
            account.create()

            account.set("store", store)
            
            ####
            if request.POST.get("place_order") and\
                request.POST.get("place_order_amount").isdigit():
                amount = int(request.POST.get("place_order_amount"))
                if amount > 0:
                    order_placed(amount, store, account)
            
            # send matt and new user a pretty email.
            # new user
            send_email_signup(account)
            # matt
            user_signup(account)

            # auto login
            user_login = login(request)
            if user_login != None:
                data = {"code":-1}
                # -1 - invalid request
                # 0 - invalid form input
                # 1 - bad login credentials
                # 2 - subscription is not active
                # 3 - success
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
                    
    else:
        store_form = StoreSignUpForm()
        account_form = AccountForm()
        subscription_form = SubscriptionForm2()

    data['store_form'] = store_form
    data['account_form'] = account_form
    data['subscription_form'] = subscription_form
    return render(request, 'public/signup.djhtml', data)

