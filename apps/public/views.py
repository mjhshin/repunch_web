from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core import mail 
from django.utils import timezone
from django.forms.util import ErrorList
from datetime import datetime
import json, pytz

from forms import ContactForm
from repunch.settings import PHONE_COST_UNIT_COST, DEBUG
from parse.auth.utils import request_password_reset
from parse.notifications import send_email_signup,\
send_email_receipt_smartphone
from apps.db_static.models import Category
from apps.accounts.forms import AccountForm
from parse.apps.stores import format_phone_number
from apps.stores.forms import StoreSignUpForm, SubscriptionForm2
from libs.repunch import rputils

from repunch.settings import STATIC_URL
from parse.auth import login
from parse.utils import make_aware_to_utc, parse
from parse.notifications import get_notification_ctx
from parse.apps.accounts.models import Account
from parse.apps.accounts import sub_type, UNLIMITED
from parse.apps.stores.models import Store, Subscription,\
Settings

def terms_mobile(request):
    return render(request, "public/terms-mobile.djhtml",
        get_notification_ctx())
        
def privacy_mobile(request):
    return render(request, "public/privacy-mobile.djhtml",
        get_notification_ctx())

def index(request):
    if request.session.get('account') is not None and\
        request.session.get('store') is not None and\
        request.session.get('subscription') is not None:
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
        
def password_reset(request):
    """
    Calls Parse's requestPasswordReset
    """
    return HttpResponse(json.dumps({"res":\
        request_password_reset(request.POST['forgot-pass-email'])}), 
        content_type="application/json")
        
        
def sign_up(request):
    """
    Creates User, store, subscription, and settings objects.
    """
    # renders the signup page on GET and returns a json object on POST.
    data = {'sign_up_nav': True}
    
    def isdigit(string):
        # use because "-1".isdigit() is False
        try:
            int(string)
        except:
            return False
        else:
            return True
            
    if request.method == 'POST' or request.is_ajax():
        # some keys are repeated so must catch this at init
        store_form = StoreSignUpForm(request.POST)
        account_form = AccountForm(request.POST)
        subscription_form = SubscriptionForm2(request.POST)
        
        
        cats =  request.POST.get("categories")
        if cats and len(cats) > 0:
            category_names = cats.split("|")[:-1]
            # make sure that there are only up to 2 categories
            while len(category_names) > 2:
                category_names.pop()
            data["category_names"] = category_names
        
        all_forms_valid = store_form.is_valid() and\
            account_form.is_valid()
        if request.POST.get("place_order"):
            data["place_order_checked"] = True
            if isdigit(request.POST.get("place_order_amount")):
                amount = int(request.POST.get("place_order_amount"))
                if amount > 0:
                    all_forms_valid = all_forms_valid and\
                        subscription_form.is_valid()
                else:
                    all_forms_valid = False
                    data["place_order_amount_error"] =\
                        "Amount must be greater than 0."
        else:
            subscription_form = SubscriptionForm2()
        
        if all_forms_valid:
            postDict = request.POST.dict()

            # create store
            tz = rputils.get_timezone(request.POST.get("zip"))
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
            if category_names:
                for name in category_names:
                    alias = Category.objects.filter(name__iexact=name)
                    if len(alias) > 0:
                        store.categories.append({
                            "alias":alias[0].alias,
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
            settings = Settings(Store=store.objectId)
            store.set('settings', settings)

            # create account
            account = Account(**postDict)
            # username = email
            account.set("username", postDict['email'])
            account.set_password(request.POST.get('password'))
            account.set("store", store)

            # create an empty subscription
            subscription = Subscription(**postDict) 
            subscription.subscriptionType = 0
            subscription.date_last_billed = timezone.now()
            subscription.Store = store.objectId 
            subscription.create()
            
            # create settings
            settings.create()
                
            # create store
            store.Settings = settings.objectId
            store.Subscription = subscription.objectId
            store.create()
            
            # add the store pointers to settings and subscription
            settings.Store = store.objectId
            settings.update()
            subscription.Store = store.objectId
            subscription.update()
            
            # create account
            account.Store = store.objectId
            account.create()
            
            # create the store ACL with the account having r/w access
            store.ACL = {
                "*": {"read": True, "write": True},
                account.objectId: {"read": True, "write": True},
            }
            store.owner_id = account.objectId
            store.update()
                
            #### MAIL CONNECTION OPEN
            conn = mail.get_connection(fail_silently=(not DEBUG))   
            
            # call this incase store_cc returns False or 
            # charge_cc returns None
            def invalid_card():
                data['store_form'] =\
                    StoreSignUpForm(store.__dict__.copy())
                errs = subscription_form._errors.setdefault(\
                    "cc_number", ErrorList())
                errs.append("Invalid credit " +\
                    "card. Please make sure that you provide " +\
                    "correct credit card information and that you " +\
                    "have sufficient funds, then try again.")
                    
                # delete the objects created!
                subscription.delete()
                settings.delete()
                store.delete()
                account.delete()
                    
                data['store_form'] = store_form
                data['account_form'] = account_form
                data['subscription_form'] = subscription_form
                return render(request,'public/signup.djhtml',data)
                       
            
            subscription.Store = store.objectId
            if request.POST.get("place_order"):
                exp = make_aware_to_utc(datetime(\
                    int(postDict['date_cc_expiration_year']),
                    int(postDict['date_cc_expiration_month']), 1), tz)
                subscription.set("date_cc_expiration", exp)
                # make sure to use the correct POST info
                subscription.first_name = request.POST['first_name2']
                subscription.last_name  = request.POST['last_name2']
                subscription.city = request.POST['city2']
                subscription.state = request.POST['state2']
                subscription.zip = request.POST['zip2']
                subscription.country = request.POST['country2']
                amount = int(request.POST.get("place_order_amount"))
                subscription.update()
                res = subscription.store_cc(\
                        subscription_form.data['cc_number'],
                        subscription_form.data['cc_cvv'])
                        
                if not res:
                    return invalid_card()
                
                if amount > 0:
                    invoice = subscription.charge_cc(\
                        PHONE_COST_UNIT_COST*amount,
                        "Order placed for " +\
                        str(amount) + " phones", "smartphone")
                        
                    if invoice:
                        send_email_receipt_smartphone(account, 
                            subscription, invoice, amount)
                    else:
                        return invalid_card()
            
            # note that username has been fed the email
            # this shouldn't change anything though shouldn't matter
            # need to put username and pass in request
            postDict['username'] = account.username
            postDict['password'] = account.password
            
            # send matt and new user a pretty email.
            send_email_signup(account)
            
            # MAIL CONNECTION CLOSE
            conn.close()

            # auto login
            user_login = login(request, postDict)
            if user_login != None:
                data = {"code":-1}
                # response effects - not login returns
                # -1 - invalid request
                # 0 - invalid form input
                # 1 - bad login credentials
                # 2 - subscription is not active
                # 3 - success (login now)
                # 4 - employee no access - never should be this though
                # 5 - employee is not approved - never should be
                if type(user_login) is int: # subscription not active
                    data['code'] = 2
                else:
                    # required for datetime awareness!
                    rputils.set_timezone(request, tz)
                    data['code'] = 3
                return HttpResponse(json.dumps(data), 
                            content_type="application/json")
           
    else:
        store_form = StoreSignUpForm()
        account_form = AccountForm()
        subscription_form = SubscriptionForm2()
        
    data['store_form'] = store_form
    data['account_form'] = account_form
    data['subscription_form'] = subscription_form
    return render(request, 'public/signup.djhtml', data)
        
