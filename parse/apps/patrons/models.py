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
        # string unique in Parse
        self.punch_code = data.get('punch_code')

        self.ReceivedMessages_ = "MessageStatus"
        self.SentMessages_ = "Message"
        self.PatronStores_ = "PatronStore"

        super(Patron, self).__init__(False, **data)
        
    @classmethod  
    def fields_required(cls):
        """
        See ParseObject for documentation.
        """
        return (cls, "first_name", "last_name", "gender",
            "date_of_birth", "punch_code")
        
    def get_fullname(self):
        return self.first_name.capitalize()+\
                " " + self.last_name.capitalize()

    def get_class(self, className):
        if className in ("Message", "MessageStatus"):
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
        # string of _User's objectId
        self.user_id = data.get("user_id")
        
        super(PunchCode, self).__init__(False, **data)
        
    @classmethod  
    def fields_required(cls):
        """
        See ParseObject for documentation.
        """
        return (cls, "punch_code", "is_taken",
            ("user_id", {"is_taken": True}))

class PatronStore(ParseObject):
    """ New class not in Django """
    def __init__(self, **data):
        self.punch_count = data.get("punch_count", 0)
        self.all_time_punches = data.get('all_time_punches', 0)
        # this is for rewards only! not offers!
        self.pending_reward = data.get("pending_reward", False)
        
        self.Patron = data.get("Patron")
        self.Store = data.get("Store")
        self.FacebookPost = data.get("FacebookPost")
        
        super(PatronStore, self).__init__(False, **data)
    
    @classmethod  
    def fields_required(cls):
        """
        See ParseObject for documentation.
        """
        return (cls, "punch_count", "all_time_punches",
            "pending_reward", "Patron", "Store")

    def get_class(self, className):
        if className == "Patron":
            return Patron
        elif className == "FacebookPost":
            return FacebookPost
        elif className == "Store":
            return getattr(import_module('parse.apps.stores.models'),
                    className)

class FacebookPost(ParseObject):
    """ Equivalence class of apps.patrons.models.FacebookPost """
    def __init__(self, **data):
        self.Patron = data.get("Patron")
        self.posted = data.get("posted")
        self.reward = data.get("reward")

        super(FacebookPost, self).__init__(False, **data)
        
    @classmethod  
    def fields_required(cls):
        """
        See ParseObject for documentation.
        """
        return (cls, "reward", "Patron")

    def get_class(self, className):
        if className == "Patron":
            return getattr(import_module('parse.apps.patrons.models'),
                                className)

