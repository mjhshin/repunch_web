"""
Parse equivalence of Django apps.employees.models
""" 

from importlib import import_module

from parse.core.models import ParseObject

class Punch(ParseObject):
    """ Equivalence class of apps.rewards.models.Punch """
    def __init__(self, **data):
        # use createdAt for date created - the timestamp
        self.punches = data.get("punches")
        
        self.Patron = data.get('Patron')
        
        super(Punch, self).__init__(False, **data)

    @classmethod  
    def fields_required(cls):
        """
        See ParseObject for documentation.
        """
        return (cls, "punches", "Patron")
        
    def get_class(self, className):
        if className == "Patron":
            return getattr(import_module('parse.apps.patrons.models'), className)
            
class RedeemReward(ParseObject):
    def __init__(self, **data):
        self.title = data.get("title")
        self.customer_name = data.get("customer_name")
        self.is_redeemed = data.get("is_redeemed", False)
        self.num_punches = data.get("num_punches")
        self.reward_id = data.get("reward_id")
        
        self.MessageStatus = data.get("MessageStatus")
        self.PatronStore = data.get('PatronStore')
        
        super(RedeemReward, self).__init__(False, **data)
        
    @classmethod  
    def fields_required(cls):
        """
        See ParseObject for documentation.
        """
        return (cls, "title", "customer_name", "is_redeemed",
            "num_punches", ("PatronStore", "reward_id"),
            ("MessageStatus", {"num_punches":0}))

    def get_class(self, className):
        if className == "PatronStore":
            return getattr(import_module('parse.apps.patrons.models'), className)
        elif className == "MessageStatus":
            return getattr(import_module('parse.apps.messages.models'), className)

