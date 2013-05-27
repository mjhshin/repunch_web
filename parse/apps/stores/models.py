"""
Parse equivalence of Django apps.stores.models
""" 
from repunch.settings import TIME_ZONE

class Store(object):
    """ Equivalence class of apps.accounts.models.Account """
    def __init__(self, data={}):
        self.objectId = data.get('objectId')
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

    def delete(self):
        # TODO 
        pass
