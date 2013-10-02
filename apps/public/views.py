from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import timezone
from django.forms.util import ErrorList
from datetime import datetime
import json, pytz

from forms import ContactForm
from repunch.settings import PHONE_COST_UNIT_COST, DEBUG
from parse.auth.utils import request_password_reset
from parse.notifications import send_email_signup,\
send_email_receipt_ipod
from apps import isdigit
from apps.db_static.models import Category
from apps.accounts.models import AssociatedAccountNonce
from apps.accounts.forms import AccountSignUpForm
from parse.apps.stores import format_phone_number
from apps.stores.forms import StoreSignUpForm, SubscriptionSignUpForm
from libs.repunch import rputils

from repunch.settings import STATIC_URL
from parse.auth import login
from parse.auth.decorators import dev_login_required
from parse.utils import make_aware_to_utc, parse, account_login
from parse.notifications import get_notification_ctx
from parse.apps.accounts.models import Account
from parse.apps.accounts import sub_type
from parse.apps.stores import IPOD
from parse.apps.stores.models import Store, Subscription,\
Settings

def terms_mobile(request):
    return render(request, "public/terms-mobile.djhtml",
        get_notification_ctx())
        
def privacy_mobile(request):
    return render(request, "public/privacy-mobile.djhtml",
        get_notification_ctx())

@dev_login_required
def index(request):
    if request.session.get('account') is not None and\
        request.session.get('store') is not None and\
        request.session.get('subscription') is not None:
        return redirect(reverse('store_index'))
        
    data = {'home_nav': True}
    return render(request, 'public/index.djhtml', data)

@dev_login_required
def learn(request):
    data = {'learn_nav': True, "sub_type": sub_type}
    return render(request, 'public/learn.djhtml', data)

@dev_login_required
def faq(request):
    data = {'faq_nav': True, 'form':ContactForm()}
    return render(request, 'public/faq.djhtml', data)

@dev_login_required
def about(request):
    data = {'about_nav': True}
    return render(request, 'public/about.djhtml', data)

@dev_login_required
def terms(request):
    return render(request, 'public/terms.djhtml')

@dev_login_required
def privacy(request):
    return render(request, 'public/privacy.djhtml')

@dev_login_required
def contact(request):
    if request.method == 'POST': 
        form = ContactForm(request.POST) 
        if form.is_valid(): 
            form.send()
            return redirect(reverse('public_thank_you'))
    else:
        form = ContactForm()

    return render(request, 'public/contact.djhtml', {'form': form, })

@dev_login_required
def thank_you(request):
    return render(request, 'public/thank_you.djhtml')

@dev_login_required
def jobs(request):
    return render(request, 'public/jobs.djhtml')

def categories(request):
    """ takes in ajax requests and returns a list of choices for
    autocompletion in json format """
    # term is the key in request.GET
    if request.method == "GET":
        categories = Category.objects.filter(name__istartswith=\
                        request.GET['term'].strip())[:8]
                        
        data = []
        for cat in categories:
            data.append(cat.name)

        return HttpResponse(json.dumps(data), 
                    content_type="application/json")
    else:
        return HttpResponse('')
     
@dev_login_required   
def password_reset(request):
    """
    Calls Parse's requestPasswordReset
    """
    return HttpResponse(json.dumps({"res":\
        request_password_reset(request.POST['forgot-pass-email'])}), 
        content_type="application/json")
        
@dev_login_required
def associated_account_confirm(request):
    """
    A helper view for sign_up. Also handles requests from signup.js
    """
    if request.method == 'POST':
        # first check the AssociatedAccountNonce
        acc_id = request.POST['aaf-account_id']
        nonce_id = request.POST['aaf-nonce']
        aa_nonce = AssociatedAccountNonce.objects.filter(\
            id=nonce_id, account_id=acc_id)
        if len(aa_nonce) > 0:
            aa_nonce = aa_nonce[0]
            # then attempt to login to parse
            username = request.POST['acc_username']
            password = request.POST['acc_password']
            # note that email is the same as username
            res = account_login(username, password)
            if 'error' not in res:
                aa_nonce.verified = True
                aa_nonce.save()
                return HttpResponse(json.dumps({"code": 0}), 
                    content_type="application/json")
                
    return HttpResponse(json.dumps({"code": 1}), 
        content_type="application/json")
    
        
@dev_login_required
def sign_up(request):
    """
    Creates User, store, subscription, and settings objects.
    """
    # renders the signup page on GET and returns a json object on POST.
    data = {'sign_up_nav': True}
            
    if request.method == 'POST':
        from_associated_account = False
        # check if this post is from the associated account dialog
        # if it is then skip form validations
        aaf_nonce_id = request.POST.get('aaf-nonce')
        aaf_account_id = request.POST.get('aaf-account_id')
        if len(aaf_nonce_id) > 0 and len(aaf_account_id) > 0:
            aa_nonce = AssociatedAccountNonce.objects.filter(\
                id=aaf_nonce_id, account_id=aaf_account_id)
            if len(aa_nonce) > 0 and aa_nonce[0].verified:
                aa_nonce[0].delete()
                from_associated_account = True
    
        # some keys are repeated so must catch this at init
        store_form = StoreSignUpForm(request.POST)
        account_form = AccountSignUpForm(request.POST)
        subscription_form = SubscriptionSignUpForm(request.POST)
        
        cats = request.POST.get("categories")
        category_names = None
        if cats and len(cats) > 0:
            category_names = cats.split("|")[:-1]
            # make sure that there are only up to 2 categories
            while len(category_names) > 2:
                category_names.pop()
            data["category_names"] = category_names
        
        if not from_associated_account:
            all_forms_valid = store_form.is_valid() and\
                account_form.is_valid()
        else:
            all_forms_valid = True
            
        ### Bad form of validation lol
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
                all_forms_valid = False
                data["place_order_amount_error"] =\
                    "Amount must be a number greater than 0."
                
        else:
            subscription_form = SubscriptionSignUpForm()
        
        if all_forms_valid:
            postDict = request.POST.dict()
            
            # check if email already taken here to handle the case where 
            # the user already has a patron/employee account 
            # but also want to sign up for a Store account
            if hasattr(account_form, "associated_account"):
                aa = account_form.associated_account
                aan = AssociatedAccountNonce.objects.create(\
                    account_id=aa.objectId)
                return HttpResponse(json.dumps({"associated_account":\
                    aa.objectId, "associated_account_nonce":aan.id,
                    "email": aa.email, "code": 0}), 
                    content_type="application/json")
            #########################################################

            # create store
            tz = rputils.get_timezone(request.POST.get("zip"))
            store = Store(**postDict)
            store.store_timezone = tz.zone
            # set defaults for these guys to prevent 
            # ParseObjects from making parse calls repeatedly
            store.punches_facebook = 1
            # format the phone number
            store.phone_number =\
                format_phone_number(request.POST['phone_number'])
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
            if not from_associated_account:
                account = Account(**postDict)
                # username = email
                account.set("username", 
                    postDict['email'].strip().lower())
                account.set("email", 
                    postDict['email'].strip().lower())
                account.set_password(request.POST.get('password'))
            else:
                account =\
                    Account.objects().get(objectId=aaf_account_id)
                
            account.set("store", store)

            # create subscription
            if request.POST.get("place_order"):
                subscription = Subscription(first_name=postDict.get("first_name2"),
                    last_name=postDict.get("last_name2"), cc_number=postDict.get("cc_number"),
                    date_cc_expiration=postDict.get("date_cc_expiration"),
                    address=postDict.get("address"), city=postDict.get("city2"),
                    state=postDict.get("state2"), zip=postDict.get("zip2"), country=postDict.get("country2"))
            else:
                subscription = Subscription() 
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
            if not from_associated_account:
                account.create()
            else:
                account.update()
            
            # create the store ACL with the account having r/w access
            store.ACL = {
                "*": {"read": True, "write": True},
                account.objectId: {"read": True, "write": True},
            }
            store.owner_id = account.objectId
            store.update()
            
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
                if not from_associated_account:
                    account.delete()
                else:
                    account.Store = None
                    account.update()
                    
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
                        str(amount) + " iPod Touch", IPOD)
                        
                    if invoice:
                        send_email_receipt_ipod(account, 
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

            # auto login
            user_login = login(request, postDict, no_recaptcha=True)
            if user_login != None:
                data = {"code":-1}
                # response to signup.js - not login returns
                # 0 - Associated account already exists
                # 2 - subscription is not active
                # 3 - success (login now)
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
        account_form = AccountSignUpForm()
        subscription_form = SubscriptionSignUpForm()
        
    data['store_form'] = store_form
    data['account_form'] = account_form
    data['subscription_form'] = subscription_form
    return render(request, 'public/signup.djhtml', data)
        
