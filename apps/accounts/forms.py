from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone
import datetime, re, pytz

from libs.repunch import rpforms, rpccutils, rputils
from libs.repunch.validators import required, alphanumeric_no_space

from parse.apps.accounts.models import Account

class PasswordForm(forms.Form):
    current = forms.CharField(\
        widget=forms.PasswordInput(attrs={'pattern':".{6,}"}))
    new = forms.CharField(min_length=6,
            widget=forms.PasswordInput(attrs={'pattern':".{6,}"}))
    confirm_new = forms.CharField(min_length=6,
            widget=forms.PasswordInput())
    
    def clean_current(self):
        """ check if the current password is corrent by logging in """
        current = self.cleaned_data.get('current')
        # TODO
        return current
        
    def clean_new(self):
        """ make sure that password is same as confirm_password """
        p1 = self.cleaned_data.get('new')
        p2 = self.data.get('confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        return p1

class EmailForm(forms.Form):
    email = forms.EmailField()
            
    """
    email = forms.EmailField()
    
    
    def __init__(self, email, *args, **kwargs):
        super(StoreForm, self).__init__(*args, **kwargs)
        self.email = email
                               
                
    def clean_email(self):
        #emails are unique - only clean email of self.email is not None
        e = self.cleaned_data.get('email')
        
        if self.email and e:
            e = e.strip().lower()
            if Account.objects().count(email=e) > 0:
                # only raise if email is not itself
                if self.email != e:
                    raise forms.ValidationError("Email is already " +\
                        "being used.")
        return e
    """
        
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
            
class LoginForm(forms.Form):
    # currently the username = email
    username = forms.CharField(validators=[required])
    password = forms.CharField(widget=forms.PasswordInput())

