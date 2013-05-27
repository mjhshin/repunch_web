"""
Provides form validation for Parse classes from app.accounts.models
"""

from parse.apps.accounts.models import Account


class AccountForm(object):
    """  Equivalence class of apps.accounts.forms.AccountForm """
    def __init__(self, data={}):
        self.account = Account(data)

    def is_valid(self, errors):
        """ 
        errors is a dictionary. Returns len(errors) == 0     
        """
        s = self.account
        if s.phone and len(s.phone) > 255:
            errors['phone'] = "Phone number cannot exceed 255 "+\
                                " characters."
        if s.email and not email_re.match(s.email):
            errors['email'] = "Please enter a valid email."
    
        # TODO VALIDATE STORE_ID AND SUBSCRIPTION_ID
        
        
        return len(errors) == 0

    def save(self):
        """ posts up the data to Parse """
        self.account.save()
        return True
