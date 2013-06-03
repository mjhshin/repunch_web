"""
Parse equivalence of Django apps.employees.models
""" 

from datetime import datetime

from parse.core.models import ParseObject

class Reward(ParseObject):
    """ Equivalence class of apps.rewards.models.Reward """
    def __init__(self, **data):
        self.reward_name = data.get("reward_name")
        self.description = data.get("description")
        self.punches = data.get("punches")
        self.reward_avatar = data.get("reward_avatar")

        self.Store = data.get("Store")

        super(Reward, self).__init__(False, **data)

    def get_absolute_url(self):
	    return reverse('reward_edit', args=[self.objectId])

    def redemption_count(self):
        return Redemption.objects().filter(Reward=self.objectId)

class Punch(ParseObject):
    """ Equivalence class of apps.rewards.models.Punch """
    def __init__(self, **data):
        self.date_punched = data.get("date_punched", datetime.now().isoformat())
        self.punches = data.get("punches")

        self.Reward = data.get("Reward")
        self.Patron = data.get("Patron")
        self.Employee = data.get("Employee")
        
        super(Punch, self).__init__(False, **data)

class Redemption(ParseObject):
    """ Equivalence class of apps.rewards.models.Redemption """
    def __init__(self, **data):
        self.date_punched = data.get("date_punched", datetime.now().isoformat())
        self.punches = data.get("punches")

        self.Reward = data.get("Reward")
        self.Patron = data.get("Patron")
        self.Employee = data.get("Employee")
        
        super(Redemption, self).__init__(False, **data)
    

