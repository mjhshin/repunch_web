"""
Parse equivalence of Django apps.stores.models
"""

class ParseStore(object):
    """ Equivalence class of apps.accounts.models.Account """
    def __init__(self, *args, **kwargs):
        self.objectId = kwargs.get('objectId')
        self.store_name = kwargs.get('store_name')
        self.city = kwargs.get('city')
        self.state = kwargs.get('state')
        self.zip = kwargs.get('zip')
        self.country = kwargs.get('country')
        self.phone_number = kwargs.get('phone_number')
        self.email = kwargs.get('email')
        self.store_description = kwargs.get('store_description')
        self.store_avatar = kwargs.get('store_avatar')
        self.active_users = kwargs.get('active_users')
        self.store_timezone = kwargs.get('store_timezone')

    def delete(self):
        # TODO 
        pass
