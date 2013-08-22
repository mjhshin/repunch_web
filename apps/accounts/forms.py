from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone
import datetime, re, pytz

from libs.repunch import rpforms, rpccutils, rputils
from libs.repunch.validators import required, alphanumeric_no_space

from parse.apps.accounts.models import Account

class AccountForm(forms.Form):   
    """
    username = forms.CharField(min_length=3, max_length=30,
                widget=forms.TextInput(attrs={'pattern':".{3,30}"}),
                validators=[required, alphanumeric_no_space])
    """
    password = forms.CharField(min_length=6,
            widget=forms.PasswordInput(attrs={'pattern':".{6,}"}),
            validators=[required, alphanumeric_no_space])
    confirm_password = forms.CharField(min_length=6,
            widget=forms.PasswordInput(),
            validators=[required, alphanumeric_no_space])
    email = forms.EmailField()

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
        if e and Account.objects().count(email=e) > 0:
            raise forms.ValidationError("Email is already being used.")
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
    username = forms.CharField(validators=[required]) #, alphanumeric_no_space])
    password = forms.CharField(widget=forms.PasswordInput(),
        validators=[required, alphanumeric_no_space])

