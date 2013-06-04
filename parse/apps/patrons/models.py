"""
Parse equivalence of Django apps.accounts.models
"""

from importlib import import_module

from parse.core.models import ParseObject
from parse.apps.accounts import ACTIVE
from parse.apps.patrons import UNKNOWN

class Patron(ParseObject):
    """ Equivalence class of apps.patrons.models.Patron """
    def __init__(self, **data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.email = data.get("email")
        self.phone_number = data.get('phone_number')
        self.gender = data.get("gender", UNKNOWN)
        self.dob = data.get("dob")
        self.status = data.get("status", ACTIVE)

        self.Stores_ = "Store"

        super(Patron, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Store":
            return getattr(import_module('parse.apps.stores.models'),
                                className)

class FacebookPost(ParseObject):
    """ Equivalence class of apps.patrons.models.FacebookPost """
    def __init__(self, **data):
        self.date_added = data.get("date_added", date.today().isoformat())
        
        self.Patron = data.get("Patron")
        self.Store = data.get("Store")

        super(FacebookPost, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Store":
            return getattr(import_module('parse.apps.stores.models'),
                                className)
        elif className == "Patron":
            return getattr(import_module('parse.apps.patrons.models'),
                                className)

