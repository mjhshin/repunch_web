from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from apps.accounts.models import SubscriptionType, Subscription
from apps.accounts.forms import AccountForm, SubscriptionForm
from apps.stores.forms import StoreSignUpForm
from forms import ContactForm
from libs.repunch import rputils

from parse.auth import login
from parse.apps.accounts.models import Account, SubscriptionType
from parse.apps.accounts import free
from parse.apps.stores.forms import StoreSignUpForm as pStoreSignUpForm
from parse.apps.accounts.forms import AccountForm as pAccountForm,\
SubscriptionForm as pSubscriptionForm

# TODO REPLACE DJANGO FORMS

def index(request):
    data = {'home_nav': True}
    return render(request, 'public/index.djhtml', data)

def learn(request):
    data = {'learn_nav': True}
    
    data['unlimited'] = SubscriptionType.UNLIMITED
    data['types'] = SubscriptionType.objects.filter(status=1).order_by('monthly_cost')
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
        # these forms are now just for rendering into html
        store_form = StoreSignUpForm(request.POST)
        account_form = AccountForm(request.POST)
        subscription_form = SubscriptionForm(request.POST)
        # if store_form.is_valid() and account_form.is_valid() and\
        #   subscription_form.is_valid(): # All validation rules pass
        
        postDict = request.POST.dict()
        # actual form validations are now done through ParseForms
        store_pf = pStoreSignUpForm(**postDict)
        account_pf = pAccountForm(**postDict)
        subscription_pf = pSubscriptionForm(**postDict)
        # pass is corresponding form's error dicts to fillem up
        # if validation fails
        if store_pf.is_valid(store_form.errors) and\
            subscription_pf.is_valid(subscription_form.errors) and\
            account_pf.is_valid(account_form.errors):

            st, su, ac = store_pf, subscription_pf, account_pf
            
            # create store
            tz = rputils.get_timezone('93003')
            st.store.store_timezone = tz.zone
            st.create()

            # TODO: need to make this transactional
            # save subscription
            su.subscription.SubscriptionType = free['objectId']
            su.create()
      
            su.subscription.store_cc(su.subscription.cc_number,
                    su.cc_cvv)
            account = ac.account
            account.Store = st.store.objectId
            account.Subscription = su.subscription.objectId
            account.set_password(request.POST.get('password'))
            account.create()

            # TODO refactor templates to use parse forms instead
            if su.subscription.cc_number:
                cc = su.subscription.cc_number
                mask = (len(cc)-4)*'*'
                mask += cc[-4:]
                subscription_form.data = subscription_form.data.copy()
                subscription_form.data['cc_number'] = mask
                # REMOVE -------------

            # auto login
            user_login = login(request, account.username, 
                            request.POST.get("password"), Account())
            if user_login != None:
                # need to set this for the auto long
                rputils.set_timezone(request, tz)
                return redirect(reverse('store_index'))
            else:
                # TODO: should never go here though
                pass
                    
    else:
        store_form = StoreSignUpForm() # An unbound form
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
