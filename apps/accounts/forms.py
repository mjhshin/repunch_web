from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone
import datetime, re, pytz

from models import Account, Settings, Subscription, SubscriptionType
from libs.repunch import rpforms, rpccutils, rputils

class AccountForm(forms.ModelForm):   

    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    def clean_password(self):
        if self.data['confirm_password'] != self.cleaned_data['password']:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data['password']
    
    class Meta:
        model = Account
        exclude = ('store', 'subscription', 'date_joined', 'last_login')
        widgets = {
            'password': forms.PasswordInput(),
        }
        
        
class SubscriptionForm(forms.ModelForm):

    cc_cvv = forms.CharField()
    recurring = forms.NullBooleanField(widget=forms.CheckboxInput(), required=True)
        
    class Meta:
        model = Subscription
        exclude = ('status', 'type', 'ppid', 'ppvalid')
        widgets = {
            'cc_expiration': rpforms.MonthYearWidget()
        }
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super(SubscriptionForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['cc_number'].required = True
        self.fields['cc_expiration'].required = True
        self.fields['address'].required = True
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['zip'].required = True
        self.fields['country'].required = True
        
        #add choices
        self.fields['country'] = forms.ChoiceField(choices=[('US', 'United States of America')])
        
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
            #raise forms.ValidationError("Error processing credit card!")
        
        return cleaned_data
    
    def clean_recurring(self):
        data = self.cleaned_data['recurring']
        
        if not data:
            raise forms.ValidationError("You must accept the Terms & Conditions to continue.")
        
        return data
    
    def clean_cc_expiration(self):
        data = self.cleaned_data['cc_expiration']
        now = datetime.datetime.now()
        if data.year == now.year:
            if data.month < now.month:
                raise forms.ValidationError("Your credit card has expired!")
            
        return data
    
    def clean_cc_number(self):
        data = self.cleaned_data['cc_number']
        data = re.sub("[^0-9]", "", data) # remove all non-numeric characters
        if rpccutils.validate_checksum(data) == False:
            raise forms.ValidationError("Enter a valid credit card number.")
        if rpccutils.validate_cc_type(data) == False:
            raise forms.ValidationError("Credit card type is not accepted.")
        
        return data
               
class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude = ('account', 'retailer_id')
            
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    def do_login(self, request):
        account = authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])
        if account is not None:
            if account.is_active:
                request.session['account'] = account
                rputils.set_timezone(request, pytz.timezone(account.store.store_timezone))
                return account
        return None

