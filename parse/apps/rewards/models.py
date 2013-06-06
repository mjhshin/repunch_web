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

    def get_class(self, className):
        if className == "Patron":
            return getattr(import_module('parse.apps.patrons.models'), className)

"""
class Reward(ParseObject):
    # Equivalence class of apps.rewards.models.Reward 
    def __init__(self, **data):
        self.reward_name = data.get("reward_name")
        self.description = data.get("description")
        self.punches = data.get("punches")
        self.redemption_count = data.get("redemption_count")

        super(Reward, self).__init__(False, **data)

    def get_absolute_url(self):
	    return reverse('reward_edit', args=[self.objectId])

        
class Redemption(ParseObject):
    # Equivalence class of apps.rewards.models.Redemption
    def __init__(self, **data):
        self.punches = data.get("punches")
        self.patron_name = data.get("patron_name")
        
        super(Redemption, self).__init__(False, **data)

"""

