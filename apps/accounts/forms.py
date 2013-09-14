from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone
import datetime, re, pytz

from libs.repunch import rpforms, rpccutils, rputils
from libs.repunch.validators import required, alphanumeric_no_space

from parse.apps.accounts.models import Account

class AccountForm(forms.Form):   
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
            acc = Account.objects().get(email=e)
            if acc and acc.Store:
                raise forms.ValidationError(\
                    "Email is already being used.")
            elif acc: # save the object for later use
                setattr(self, "associated_account", acc)
        return e

    """
    def clean_username(self):
    # usernames are unique
        u = self.cleaned_data.get('username')
        if u and Account.objects().count(username=u) > 0:
            raise forms.ValidationError("Username is already being"+\
                                        " used.")
        return u
    """
            
class LoginForm(forms.Form):
    # currently the username = email
    username = forms.CharField(validators=[required])
    password = forms.CharField(widget=forms.PasswordInput())

