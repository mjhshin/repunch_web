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
        self.phone_number = data.get('phone_number')
        self.gender = data.get("gender", UNKNOWN)
        self.dob = data.get("dob")
        self.status = data.get("status", ACTIVE)

        self.Stores_ = "Store"
        self.Feedbacks_ = "Feedback"
        self.FacebookPosts_ = "FacebookPost"
        self.PatronStores_ = "PatronStore"

        super(Patron, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Store":
            return getattr(import_module('parse.apps.stores.models'),
                                className)
        elif className == "Feedback":
            return getattr(import_module('parse.apps.messages.models'),
                                className)
        elif className == "PatronStore":
            return PatronStore
        elif className == "FacebookPost":
            return FacebookPost

class PatronStore(ParseObject):
    """ New class not in Django """
    def __init__(self, **data):
        self.Patron = data.get("Patron")
        self.Store = data.get("Store")
        self.punch_count data.get("punch_count", 0)
    def get_class(self, className):
        if className == "Store":
            return getattr(import_module('parse.apps.stores.models'),
                                className)
        elif className == "Patron":
            return Patron

class FacebookPost(ParseObject):
    """ Equivalence class of apps.patrons.models.FacebookPost """
    def __init__(self, **data):
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

