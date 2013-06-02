from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone
import datetime, re, pytz

from models import Account, Settings, Subscription, SubscriptionType
from libs.repunch import rpforms, rpccutils, rputils

from parse.apps.accounts.models import Account
from parse.auth import login

class AccountForm(forms.Form):   
    username = forms.CharField(min_length=3, max_length=30,
                widget=forms.TextInput(attrs={'pattern':".{3,30}"}))
    password = forms.CharField(min_length=6,
            widget=forms.PasswordInput(attrs={'pattern':".{6,}"}))
    confirm_password = forms.CharField(min_length=6,
            widget=forms.PasswordInput())
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    phone_number = forms.CharField()

    def clean_password(self):
        """ make sure that password is same as confirm_password """
        p1 = self.cleaned_data.get('password')
        p2 = self.data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        return p1
    
    def clean_email(self):
        """ emails are unique """
        e = self.cleaned_data.get('email')
        if e and Account.objects().get(email=e):
            raise forms.ValidationError("Email is already being used")
        return e

    def clean_username(self):
        """ usernames are unique """
        u = self.cleaned_data.get('username')
        if u and Account.objects().get(username=u):
            raise forms.ValidationError("Username is already being"+\
                                        " used")
        return u
        
class SubscriptionForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=100)
    cc_number = forms.CharField(max_length=255)
    cc_expiration = forms.DateField(widget=rpforms.MonthYearWidget())
    address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    state = forms.CharField(max_length=255)
    zip = forms.CharField(max_length=255)
    country = forms.ChoiceField(choices=[('US', 
                                    'United States of America')])

    cc_cvv = forms.CharField()
    recurring = forms.NullBooleanField(widget=forms.CheckboxInput())
    
    def clean(self, *args, **kwargs):
        super(SubscriptionForm, self).clean()
        cleaned_data = self.cleaned_data
        
        # if cc_number doesn't exists, it is because we already 
        # have an error
        if 'cc_number' in cleaned_data:
            cc = cleaned_data['cc_number']
            mask = (len(cc)-4)*'*'
            mask += cc[-4:]
            cleaned_data['cc_number'] = mask
        
            # credit card processing will go here
            # raise forms.ValidationError("Error processing credit"+\
            #                            " card!")
        
        return cleaned_data
    
    def clean_recurring(self):
        data = self.cleaned_data['recurring']
        if not data:
            raise forms.ValidationError("You must accept the Terms"+\
                                    " & Conditions to continue.")
        return data
    
    def clean_cc_expiration(self):
        data = self.cleaned_data['cc_expiration']
        now = datetime.datetime.now()
        if data.year == now.year:
            if data.month < now.month:
                raise forms.ValidationError("Your credit card has"+\
                                            " expired!")
            
        return data
    
    def clean_cc_number(self):
        data = self.cleaned_data['cc_number']
        data = re.sub("[^0-9]", "", data) 

        if rpccutils.validate_checksum(data) == False:
            raise forms.ValidationError("Enter a valid credit card"+\
                                        " number.")
        if rpccutils.validate_cc_type(data) == False:
            raise forms.ValidationError("Credit card type is not"+\
                                        " accepted.")
        
        return data
               
class SettingsForm(forms.Form):
    punches_customer = forms.IntegerField(label=\
                        'Number of separate times a customer can'+\
                        ' receive punches per day', min_value=0)
    punches_employee = forms.IntegerField(label=\
                        'Number of punches allowed by an employee'+\
                        ' at one time', min_value=0)
    punches_facebook = forms.IntegerField(label=\
                        'Free Punch Allowance for Facebook',
                                        min_value=0)
            
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    
    def do_login(self, request):
        account = login(request, request.POST.get('username'), 
                            request.POST.get("password"), Account())
        if account:
            rputils.set_timezone(request, 
            pytz.timezone(account.get('store').get('store_timezone')))
        return account

