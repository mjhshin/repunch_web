from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login

from apps.accounts.models import SubscriptionType, Subscription
from apps.accounts.forms import AccountForm, SubscriptionForm
from apps.stores.forms import StoreSignUpForm
from forms import ContactForm
from libs.repunch import rputils

from parse.apps.accounts import free
from parse.apps.stores.forms import StoreForm as pStoreForm
from parse.apps.accounts.forms import AccountForm as pAccountForm,\
SubscriptionForm as pSubscriptionForm

def index(request):
    data = {'home_nav': True}
    return render(request, 'public/index.djhtml', data)

def learn(request):
    data = {'learn_nav': True}
    
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
        store_form = pStoreSignUpForm(request.POST)
        account_form = pAccountForm(request.POST)
        subscription_form = pSubscriptionForm(request.POST)
        # if store_form.is_valid() and account_form.is_valid() and\
        #   subscription_form.is_valid(): # All validation rules pass

        # actual form validations are now done through ParseForms
        store_pf = StoreForm(request.POST)
        account_pf = AccountForm(request.POST)
        subscription_pf = SubscriptionForm(request.POST)
        # pass is corresponding form's error dicts to fillem up
        # if validation fails
        if store_pf.is_valid(store_form.errors) and\
            subscription_pf.is_valid(subscription_form and\
            account_pf.is_valid(account_form.errors) ):

            st, su, ac = store_pf, subscription_pf, account_pf
            
            # save store
            tz = rputils.get_timezone('93003')
            st.store.store_timezone = tz.zone
            st.save()

            # TODO: need to make this transactional
            # save subscription
            su.subscription.type_id = free.objectId
            su.save()

            # TODO refactor templates to use parse forms instead
            if su.subscription.cc_number:
                cc = su.subscription.cc_number
                mask = (len(cc)-4)*'*'
                mask += cc[-4:]
                subscription_form.data['cc_number'] = mask
            # REMOVE -------------
            
            su.subscription.store_cc(subscription_form.data['cc_number'], subscription_form.data['cc_cvv']);
                      
            acount = ac.account
            account.store_id = store_pf.store.objectId
            account.subscription_id = su.subscription
            account.set_password(request.POST.get('password'))
            account.save()

            #auto login
            user_login = authenticate(username=account.username,
                    password=request.POST.get('password'))
            if user_login != None:
                try:
                    login(request, user_login) #log into the system
                except Exception as e:
                    print(e)
                request.session['account'] = account
                
                #need to set this for the auto long
                rputils.set_timezone(request, tz)
                return redirect(reverse('store_index'))
            else:
                # TODO: handle this
                # should never go here though
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
