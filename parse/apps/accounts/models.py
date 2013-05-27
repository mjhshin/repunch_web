"""
Keep tabs on Parse Classes and attributes equivalent to the Django
models.
"""

class Account(object):
    """
    Equivalence class of apps.accounts.models.Account
    """
    def __init__(self, *args, **kwargs):
        self.objectId = **kwargs.get('objectId')
        self.username = **kwargs.get('username')
        self.password = **kwargs.get('password')
        self.email = **kwargs.get('email')
        self.first_name = **kwargs.get('first_name')
        self.last_name = **kwargs.get('last_name')
        self.phone = **kwargs.get('phone')
        self.store_id = **kwargs.get('store_id')

    def get_settings(self):
        # TODO
        return None
        
    def get_sents_available(self):
        """
        returns how many messages can be sent this month
        """
        # TODO
        return None
    
    def is_free(self):
        # TODO
        return True

    def upgrade(self):
        # TODO
        return False

    
    
    





