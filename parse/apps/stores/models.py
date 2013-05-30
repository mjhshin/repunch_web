"""
Parse equivalence of Django apps.stores.models
""" 
from importlib import import_module

from repunch.settings import TIME_ZONE
from parse.utils import parse
from parse.core.models import ParseObject

DAYS = ((1, 'Sunday'),
		(2, 'Monday'),
        (3, 'Tuesday'),
        (4, 'Wednesday'),
        (5, 'Thursday'),
        (6, 'Friday'),
        (7, 'Saturday'))

SHORT_DAYS = ((1, 'Sun'),
		(2, 'Mon'),
        (3, 'Tues'),
        (4, 'Wed'),
        (5, 'Thurs'),
        (6, 'Fri'),
        (7, 'Sat'))

class Store(ParseObject):
    """ Equivalence class of apps.stores.models.Store """
    def __init__(self, data={}):
        self.store_name = data.get('store_name')
        self.city = data.get('city')
        self.state = data.get('state')
        self.zip = data.get('zip')
        self.country = data.get('country')
        self.phone_number = data.get('phone_number')
        self.email = data.get('email')
        self.store_description = data.get('store_description')
        self.store_avatar = data.get('store_avatar')
        self.active_users = data.get('active_users', 0)
        self.store_timezone = data.get('store_timezone', TIME_ZONE)

        self.Patrons_ = "Patron"
        self.patrons = None

        super(Store, self).__init__(data)

    def get_class(self, className):
        if className == "Patron":
            return getattr(import_module('parse.apps.patrons.models'),
                                className)

class Hours(ParseObject):
    """ Equivalence class of apps.stores.models.Hours """

    def __init__(self, data={}):
        self.days = data.get('days')
        self.open = data.get('open')
        self.close = data.get('close')
        self.list_order = data.get('list_order')

        self.Store = data.get("Store")
        self.store = None

        super(Hours, self).__init__(data)





