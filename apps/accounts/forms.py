from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone
import datetime, re, pytz

from libs.repunch import rpforms, rpccutils, rputils
from libs.repunch.validators import required, alphanumeric_no_space

from parse.apps.accounts.models import Account
from parse.utils import account_login

class PasswordForm(forms.Form):
    current = forms.CharField(widget=forms.PasswordInput())
    new = forms.CharField(min_length=6,
            widget=forms.PasswordInput(attrs={'pattern':".{6,}"}))
    confirm_new = forms.CharField(widget=forms.PasswordInput())
        
    def __init__(self, account, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)
        self.account = account
        
    def clean_current(self):
        """ check if the current password is corrent by logging in """
        current = self.cleaned_data.get('current')
        if 'error' in account_login(self.account.username, current):
            raise forms.ValidationError("Incorrect password.")
        return current
        
    def clean_new(self):
        """ make sure that password is same as confirm_password """
        p1 = self.cleaned_data.get('new')
        p2 = self.data.get('confirm_new')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match.")
        return p1

class EmailForm(forms.Form):
    email = forms.EmailField()
            
    def __init__(self, account, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        self.account = account
                
    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if Account.objects().count(email=email) > 0:
            if self.account.email != email:
                raise forms.ValidationError("Email is already " +\
                    "being used.")
        return email
        
class AccountSignUpForm(forms.Form):   
    """
    Note that usernames can have leading, b/w, and trailing spaces
    but must have at least 1 no spaces.
    
    Passwords, on the other hand, can be all spaces!
    """
    password = forms.CharField(min_length=6,
            widget=forms.PasswordInput(attrs={'pattern':".{6,}"}))
    confirm_password = forms.CharField(min_length=6,
            widget=forms.PasswordInput())
    email = forms.EmailField()

    def clean_password(self):
        """ make sure that password is same as confirm_password """
        p1 = self.cleaned_data.get('password')
        p2 = self.data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        return p1
    
    def clean_email(self):
        # If an Account exist already with a Store object - then bad
        e = self.cleaned_data.get('email')
        if e:
            e = e.strip().lower()
            acc = Account.objects().get(email=e)
            if acc and acc.Store:
                raise forms.ValidationError(\
                    "Email is already being used.")
            elif acc: # save the object for later use
                setattr(self, "associated_account", acc)
        return e

class EmployeeAccountSignUpForm(AccountSignUpForm):
    """
    Unlike int AccountSignUpForm, we are doing the registration in
    the cloud.    
    """
    def clean_email(self):
        return self.cleaned_data.get('email')

            
class LoginForm(forms.Form):
    # currently the username = email
    username = forms.CharField(validators=[required])
    password = forms.CharField(widget=forms.PasswordInput())

