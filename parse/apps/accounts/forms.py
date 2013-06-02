"""
Provides form validation for Parse classes from app.accounts.models
"""

import re, pytz
from datetime import datetime
from django.core.validators import email_re

from parse.auth import login
from parse.apps.accounts.models import Account, Subscription, Settings
from libs.repunch import rpforms, rpccutils, rputils

class LoginForm(object):
    """  Equivalence class of apps.accounts.forms.LoginForm """
    def __init__(self, **data):
        self.username = data.get('username')
        self.password = data.get('password')
    
    def do_login(self, request):
        account = login(request, request.POST.get('username'), 
                            request.POST.get("password"), Account())
        rputils.set_timezone(request, 
            pytz.timezone(account.get('store').get('store_timezone')))
        return account

    def is_valid(self):
        # TODO
        return True

class SubscriptionForm(object):
    """  Equivalence class of apps.accounts.forms.SubscriptionForm """
    def __init__(self, instance=None, **data):
        if instance:
            self.subscription = Subscription(**instance.__dict__)
            self.subscription.update_locally(data, False)
        else:
            self.subscription = Subscription(**data)
        self.cc_cvv = data.get("cc_cvv")
        self.recurring = data.get("recurring")
        

    def is_valid(self, errors):
        """ errors is a dictionary. Returns len(errors) == 0 
        TODO: credit card processing will go here after 
        cleaning cc_number
        """    
        s = self.subscription
        # cc_number
        # remove all non-numeric characters
        s.cc_number = re.sub("[^0-9]", "", s.cc_number) 
        if rpccutils.validate_checksum(s.cc_number) == False:
            errors["cc_number"] = "Enter a valid credit card number."
            s.cc_number = None
        if rpccutils.validate_cc_type(str(s.cc_number)) == False:
            errors["cc_number"] = "Credit card type is not "+\
                                    "accepted."
            s.cc_number = None
    
        # cc_expiration
        now = datetime.now()
        if s.cc_expiration_year == now.year:
            if s.cc_expiration_month < now.month:
                errors["cc_expiration"] = "Your credit card has"+\
                                        " expired!"

        # recurring
        if not self.recurring:
            errors["recurring"] = "You must accept the Terms &"+\
                    " Conditions to continue."

        return len(errors) == 0
        
    def create(self):
        """ create a new Subscription in Parse """
        self.subscription.create()

    def update(self):
        """ update an existing Subscription in Parse """
        self.subscription.update()

class AccountForm(object):
    """  Equivalence class of apps.accounts.forms.AccountForm """
    def __init__(self, **data):
        self.account = Account(**data)

    def is_valid(self, errors):
        """ errors is a dictionary. Returns len(errors) == 0 """
        s = self.account
        if s.phone_number and len(s.phone_number) > 255:
            errors['phone_number'] = "Phone number cannot exceed 255 "+\
                                " characters."
        if s.email and not email_re.match(s.email):
            errors['email'] = "Please enter a valid email."
    
        # TODO VALIDATE STORE_ID AND SUBSCRIPTION_ID
        # username and email should needs to be unique
        
        return len(errors) == 0

    def create(self):
        """ create a new Account in Parse """
        return self.account.create()

    def update(self):
        """ update an existing Account in Parse """
        self.account.update()

class SettingsForm(object):
    """  Equivalence class of apps.accounts.forms.SettingsForm """
    def __init__(self, instance=None, **data):
        if instance:
            self.settings = Settings(**instance.__dict__)
            self.settings.update_locally(data, False)
        else:
            self.settings = Settings(**data)

    def is_valid(self, errors):
        """ errors is a dictionary. Returns len(errors) == 0 """
        s = self.settings
        lst = (s.get('punches_customer'), s.get('punches_employee'),
                s.get('punches_facebook'))

        for each in lst:
            try:
                num = int(each)
            except TypeError:
                errors[each] =\
                            "This field must be a number."
            else:
                if num < 0:
                    errors[each] =\
                            "Cannot be a negative number."
                
        return len(errors) == 0

    def create(self):
        """ create a new Settings in Parse """
        self.settings.create()

    def update(self):
        """ update an existing Settings in Parse """
        self.settings.update()

