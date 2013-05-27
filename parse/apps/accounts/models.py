"""
Parse equivalence of Django apps.accounts.models
"""

class ParseAccount(object):
    """ Equivalence class of apps.accounts.models.Account """
    def __init__(self, *args, **kwargs):
        self.objectId = kwargs.get('objectId')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.email = kwargs.get('email')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.phone = kwargs.get('phone')

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
    
    def delete(self):
        # TODO
        pass

    
class ParseSubscription(object):
    """ Equivalence class of apps.accounts.models.Subscription """
    def __init__(self, *args, **kwargs):
        self.objectId = kwargs.get('objectId')
        self.status = kwargs.get('status')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.cc_number = kwargs.get('cc_number')
        self.cc_expiration = kwargs.get('cc_expiration')
        self.address = kwargs.get('address')
        self.city = kwargs.get('city')
        self.state = kwargs.get('state')
        self.zip = kwargs.get('zip')
        self.country = kwargs.get('country')
        self.ppid = kwargs.get('ppid')
        self.ppvalid = kwargs.get('ppvalid')

        self.type_id = kwargs.get('subscriptionType_id')
    
    def store_cc(self, cc_number, cvv):
        """ store credit card info """
        # TODO
        return False

    def charge_cc(self):
        # TODO
        pass

    def delete(self):
        # TODO
        pass

class ParseSubscriptionType(object):
    """ Equivalence class of apps.accounts.models.SubscriptionType """
    def __init__(self, *args, **kwargs):
        self.objectId = kwargs.get('objectId')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.monthly_cost = kwargs.get('monthly_cost', default=0)
        self.max_users = kwargs.get('max_users')
        self.max_messages = kwargs.get('max_messages')
        self.level = kwargs.get('level')
        self.status = kwargs.get('status')
        
