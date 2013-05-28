"""
Provides form validation for Parse classes from app.accounts.models
"""

from django.core.validators import email_re
from json import dumps

from parse.apps.stores.models import Store

class StoreForm(object):
    """ Equivalence class of apps.stores.forms.StoreForm """
    def __init__(self, data={}):
        self.store = Store(data)

    def is_valid(self, errors):
        """ 
        errors is a dictionary. Returns len(errors) == 0     
        """
        s = self.store
        f = ['store_name', 'street', 'city', 'state', 'zip',
                'country', 'phone_number', 'email', 'store_avatar']
        for e in f:
            if s.__dict__.get(e) and len(s.__dict__.get(e)) > 255:
                errors[s] = "%s cannot exceed 255 characters." % (x,)
        if s.email and not email_re.match(s.email):
            errors['email'] = "Please enter a valid email."
        
        return len(errors) == 0

    def create(self):
        """ create a new Store in Parse """
        self.store.create()
        return True








