"""
Parse equivalence of Django apps.accounts.models
"""

from datetime import date 
from importlib import import_module

from parse.core.models import ParseObject

class Patron(ParseObject):
    """ Equivalence class of apps.patrons.models.Patron """

    UNKNOWN = "Unknown"
    MALE = "Male"
    FEMALE = "Female"

    ACTIVE = "Active"
    INACTIVE = "Inactive"

    def __init__(self, **data):
        self.name = data.get('name')
        self.email = data.get("email")
        self.gender = data.get("gender", UNKNOWN)
        self.dob = data.get("dob")
        self.status = data.get("status", ACTIVE)
        self.date_added = data.get("date_added", date.today().isoformat())

        self.Stores_ = "Store"

        super(Patron, self).__init__(**data)

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

        super(FacebookPost, self).__init__(**data)

