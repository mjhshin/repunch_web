from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from datetime import datetime
import json

from parse.apps.accounts import order_placed
from apps.db_static.models import Category
from apps.accounts.forms import AccountForm
from apps.stores.forms import StoreSignUpForm, SubscriptionForm2
from forms import ContactForm
from libs.repunch import rputils

from parse.auth import login
from parse.apps.accounts.models import Account
from parse.apps.accounts import sub_type, UNLIMITED, ACTIVE
from parse.apps.stores.models import Store, Subscription,\
Settings

def index(request):
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

def sign_up(request):
    data = {'sign_up_nav': True}
    
    if request.method == 'POST':
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
            tz = rputils.get_timezone('93003')
            store = Store(**postDict)
            store.store_timezone = tz.zone
            store.Subscription = subscription.objectId
            store.punches_facebook = 0
            store.categories = []
            names = request.POST.get("categories")
            if names:
                for name in names.split(",")[:-1]:
                    alias = Category.objects.filter(name__iexact=\
                                                    name)[0].alias
                    store.categories.append({
                        "alias":alias,
                        "name":name })
            store.create()    
            
            if request.POST.get("place_order") and\
                request.POST.get("place_order_amount").isdigit():
                amount = int(request.POST.get("place_order_amount"))
                if amount > 0:
                    order_placed(amount, store)

            # create settings
            settings = Settings.objects().create(retailer_pin=\
                        rputils.generate_id(), punches_customer=1,
                        punches_employee=5, Store=store.objectId)
            store.Settings = settings.objectId
            store.set('settings', settings)
            # set defaults for these guys to prevent 
            # ParseObjects from making parse calls repeatedly
            store.set("description", "The " + store.store_name)
            store.set("hours", [])
            store.set("rewards", [])
            store.update()

            # create account
            account = Account(**postDict)
            account.Store = store.objectId
            account.account_type = "store"
            account.set_password(request.POST.get('password'))
            account.create()

            # set for storing in session
            account.set("store", store)

            # auto login
            user_login = login(request, account.username, 
                            request.POST.get("password"), account)
            if user_login != None:
                # need to set this for the auto long
                rputils.set_timezone(request, tz)
                return redirect(reverse('store_index'))
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






