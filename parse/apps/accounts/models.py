"""
Parse equivalence of Django apps.accounts.models
"""

from importlib import import_module

from parse.core.models import ParseObject, ParseObjectManager
from parse.apps.accounts import sub_type, FREE
from parse.utils import parse

class Account(ParseObject):
    """ Equivalence class of apps.accounts.models.Account 
    This account is special in that it is the model for
    Parse.User.
        
    IMPORTANT!
    The Parse table of this class is the Parse.User table in the DB!
    So don't go looking for an Account class in the Data Browser!
    """

    def __init__(self, **data):
        # note that we are using the email as the username also
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')

        self.Store = data.get('Store')
        self.Patron = data.get('Patron')
        self.Employee = data.get('Employee')

        super(Account, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Patron":
            return getattr(import_module('parse.apps.patrons.models'), className)
        elif className == "Employee":
            return getattr(import_module('parse.apps.employees.models'), className)
        elif className == "Store":
            return getattr(import_module('parse.apps.stores.models'), className)

    def set_password(self, new_pass):
        """ sets the password to a hashed new_pass """
        # self.password = hash_password(new_pass)
        self.password = new_pass

    def get_sents_available(self):
        """
        returns how many messages can be sent this month
        """
        # TODO
        return None
    
    def is_free(self):
		return self.get('store').get('subscription').get('subscriptionType') == 0


