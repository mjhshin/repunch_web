from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login

from apps.accounts.models import SubscriptionType, Subscription
from apps.accounts.forms import AccountForm, SubscriptionForm
from apps.stores.forms import StoreSignUpForm
from forms import ContactForm
from libs.repunch import rputils

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
    
    if request.method == 'POST': # If the form has been submitted...
        store_form = StoreSignUpForm(request.POST)
        account_form = AccountForm(request.POST)
        subscription_form = SubscriptionForm(request.POST)
        if store_form.is_valid() and account_form.is_valid() and subscription_form.is_valid(): # All validation rules pass
            store = store_form.save(commit=False)
            
            tz = rputils.get_timezone('93003')
            store.store_timezone = tz.zone
            store.save()
            
            if store != None:
                try:
                    # TODO: need to make this transactional
                    #create subscription
                    subscription = subscription_form.save(commit=False);
                    subscription.status = 1;
                    subscription.type = SubscriptionType.objects.filter(monthly_cost=0,status=1).get();
                    subscription.save();
                    
                    subscription.store_cc(subscription_form.data['cc_number'], subscription_form.data['cc_cvv']);
                    
                    account = account_form.save(commit=False)               
                    account.store = store
                    account.subscription = subscription
                    account.set_password(request.POST.get('password'))
                    account.is_active = 1
                    
                    account.save()
                                        
                    #auto login
                    user_login = authenticate(username=account.username, password=request.POST.get('password'))
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
                        pass
                        
                except Exception:
                    store.delete()
                    # TODO: send error
            
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
