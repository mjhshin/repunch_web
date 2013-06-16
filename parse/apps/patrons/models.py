"""
Parse equivalence of Django apps.accounts.models
"""

from importlib import import_module

from parse.core.models import ParseObject
from parse.apps.patrons import UNKNOWN

class Patron(ParseObject):
    """ Equivalence class of apps.patrons.models.Patron """
    def __init__(self, **data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.gender = data.get("gender", UNKNOWN)
        self.date_of_birth = data.get("date_of_birth")
        self.facebook_id = data.get('facebook_id')
        # string
        self.punch_code = data.get('punch_code')

        self.Feedbacks_ = "Feedback"
        self.PatronStores_ = "PatronStore"

        super(Patron, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Feedback":
            return getattr(import_module('parse.apps.messages.models'),
                                className)
        elif className == "PatronStore":
            return PatronStore

class PunchCode(ParseObject):
    """ New class not in Django """
    def __init__(self, **data):
        # string from 00000 to 99999
        self.punch_code = data.get("punch_code")
        self.is_taken = data.get("is_taken", False)
        # string of _User's username
        self.username = data.get("username")
        
        super(PunchCode, self).__init__(False, **data)

class PatronStore(ParseObject):
    """ New class not in Django """
    def __init__(self, **data):
        self.Patron = data.get("Patron")
        # Store's objectId as string
        self.Store = data.get("Store")
        self.punch_count = data.get("punch_count", 0)
        self.all_time_punches = data.get('all_time_punches', 0)
        
        super(PatronStore, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Patron":
            return Patron
        elif className == "Store":
            return getattr(import_module('parse.apps.stores.models'),
                    className)

class FacebookPost(ParseObject):
    """ Equivalence class of apps.patrons.models.FacebookPost """
    def __init__(self, **data):
        self.Patron = data.get("Patron")

        super(FacebookPost, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Patron":
            return getattr(import_module('parse.apps.patrons.models'),
                                className)

