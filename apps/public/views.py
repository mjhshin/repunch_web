from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
import json

from apps.db_static.models import Category
from apps.accounts.forms import AccountForm
from apps.stores.forms import StoreSignUpForm, SubscriptionForm
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
        store_form = StoreSignUpForm(request.POST)
        account_form = AccountForm(request.POST)
        subscription_form = SubscriptionForm(request.POST)

        if store_form.is_valid() and account_form.is_valid() and\
           subscription_form.is_valid():
            postDict = request.POST.dict()

            # TODO: need to make this transactional
            # create subscription
            subscription = Subscription(**postDict)
            subscription.subscriptionType = 0
            subscription.create()
            subscription.store_cc(subscription_form.data['cc_number'],
                            subscription_form.data['cc_cvv'])

            # create store
            tz = rputils.get_timezone('93003')
            store = Store(**postDict)
            store.store_timezone = tz.zone
            store.Subscription = subscription.objectId
            # categories need to be properly formatted 
            # from "sunny beach,sun dawn" TODO
            # to [{alias:"sunny", name:"sunny beach"}...]
            # store.categories = categories
            store.punches_facebook = 0
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
                # TODO: should never go here though
                pass
                    
    else:
        store_form = StoreSignUpForm()
        account_form = AccountForm()
        subscription_form = SubscriptionForm()

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
        categories = Category.objects.filter(name__startswith=\
                        request.GET['term'])[:6]
        data = []
        for each in categories:
            data.append(name)

        # TODO remove hen data has been added
        data = [ ("Amateur Sports Teams", 'amateursportsteams'),
            ("Amusement Parks", 'amusementparks'),
            ("Aquariums", 'aquariums'),
            ('Archery', 'archery'),
            ('Badminton', 'badminton'),
            ('Beaches', 'beaches'),
            ('Bike Rentals', 'bikerentals'),
            ('Boating', 'boating'),
            ('Bowling', 'bowling'),
            ('Climbing', 'climbing'),
            ('Disc Golf', 'discgolf'),
            ('Diving', 'diving') ]
        d = []
        for each in data:
            d.append(each[0])
        # -------------------

        return HttpResponse(json.dumps(d), 
                    content_type="application/json")
    else:
        return HttpResponse('')






