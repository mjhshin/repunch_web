"""
Parse equivalence of Django apps.accounts.models
"""

class ParseAccount(object):
    """ Equivalence class of apps.accounts.models.Account """
    def __init__(self, data):
        self.objectId = data.get('objectId')
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.phone = data.get('phone')

        self.store_id = **data.get('store_id')

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
    def __init__(self, data):
        self.objectId = data.get('objectId')
        self.status = data.get('status')
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.cc_number = data.get('cc_number')
        self.cc_expiration = data.get('cc_expiration')
        self.address = data.get('address')
        self.city = data.get('city')
        self.state = data.get('state')
        self.zip = data.get('zip')
        self.country = data.get('country')
        self.ppid = data.get('ppid')
        self.ppvalid = data.get('ppvalid')

        self.type_id = data.get('subscriptionType_id')
    
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
    def __init__(self, data):
        self.objectId = data.get('objectId')
        self.name = data.get('name')
        self.description = data.get('description')
        self.monthly_cost = data.get('monthly_cost', default=0)
        self.max_users = data.get('max_users')
        self.max_messages = data.get('max_messages')
        self.level = data.get('level')
        self.status = data.get('status')
        
