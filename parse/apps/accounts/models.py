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
    
    Also, emailVerified and authData should not be touched!
    emailVerified is a reserved word and authData must not be None.
    """

    def __init__(self, **data):
        # note that we are using the email as the username also
        # also note that emails in Parse are case sensitive! 
        # so we must always lower email addresses
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')

        self.Store = data.get('Store')
        self.Patron = data.get('Patron')
        self.Employee = data.get('Employee')

        super(Account, self).__init__(False, **data)
        
    @classmethod  
    def fields_required(cls):
        """
        See ParseObject for documentation.
        """
        # note that password is not included because it is always
        # treated as if it were null
        
        # email cannot be null if authData is null
        return (cls, "username", ("email", {"authData": None}),
            ["Store", "Patron", "Employee"])
    
    def update(self, save_password=False):
        # get the formated data to be put in the request
        data = self._get_formatted_data()
        
        # this is actually unnecessary since parse will not save 
        # the given password if it is None.
        if not save_password:
            del data['password']
            
        res = parse("PUT", self.path() + "/" + self.objectId, data)
        
        # always set the password to None to prevent passing it around in comet receive
        if self.__dict__.get("password") is not None:
            self.password = None
        
        if res and "error" not in res:
            self.update_locally(res, False)
            return True

        return False

    def get_class(self, className):
        if className == "Patron":
            return getattr(import_module('parse.apps.patrons.models'), className)
        elif className == "Employee":
            return getattr(import_module('parse.apps.employees.models'), className)
        elif className == "Store":
            return getattr(import_module('parse.apps.stores.models'), className)

    def set_password(self, new_pass):
        """ may want to do some extra stuff here in the future """
        self.password = new_pass
    
    def is_free(self):
		return self.get('store').get('subscription').get('subscriptionType') == 0


