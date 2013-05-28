"""
Provides form validation for Parse classes from app.accounts.models
"""

import re
from datetime import datetime
from django.core.validators import email_re

from parse.apps.accounts.models import Account, Subscription
from libs.repunch import rpforms, rpccutils, rputils

class SubscriptionForm(object):
    """  Equivalence class of apps.accounts.forms.SubscriptionForm """
    def __init__(self, data={}):
        self.subscription = Subscription(data)
        self.cc_cvv = data.get("cc_cvv")
        self.recurring = data.get("recurring")

    def is_valid(self, errors):
        """ errors is a dictionary. Returns len(errors) == 0 
            TODO : credit card processing will go here after cleaning
            cc_number
        """    
        s = self.subscription
        # cc_number
        # remove all non-numeric characters
        s.cc_number = re.sub("[^0-9]", "", s.cc_number) 
        if rpccutils.validate_checksum(s.cc_number) == False:
            errors["cc_number"] = "Enter a valid credit card number."
            s.cc_number = None
        if rpccutils.validate_cc_type(s.cc_number) == False:
            errors["cc_number"] = "Credit card type is not "+\
                                    "accepted."
            s.cc_number = None
    
        # cc_expiration
        now = datetime.now()
        if s.cc_expiration_year == now.year:
            if s.cc_expiration_month < now.month:
                errors["cc_expiration"] = "Your credit card has"+\
                                        " expired!"
        
    def save(self):
        """ create a new subscription in Parse """
        self.subscription.save()

class AccountForm(object):
    """  Equivalence class of apps.accounts.forms.AccountForm """
    def __init__(self, data={}):
        self.account = Account(data)

    def is_valid(self, errors):
        """ errors is a dictionary. Returns len(errors) == 0 """
        s = self.account
        if s.phone and len(s.phone) > 255:
            errors['phone'] = "Phone number cannot exceed 255 "+\
                                " characters."
        if s.email and not email_re.match(s.email):
            errors['email'] = "Please enter a valid email."
    
        # TODO VALIDATE STORE_ID AND SUBSCRIPTION_ID
        # username should also be unique
        
        return len(errors) == 0

    def save(self):
        """ create a new Account in Parse """
        return self.account.save()


