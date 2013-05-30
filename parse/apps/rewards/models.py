"""
Parse equivalence of Django apps.employees.models
""" 

from datetime import datetime

from parse.core.models import ParseObject
from parse.utils import parse

class Reward(ParseObject):
    """ Equivalence class of apps.rewards.models.Reward """
    def __init__(self, data={}):
        self.name = data.get("name")
        self.description = data.get("description")
        self.punches = data.get("punches")
        self.reward_avatar = data.get("reward_avatar")

        self.Store = data.get("Store")

        super(Reward, self).__init__(data)

    def get_absolute_url(self):
		return reverse('reward_edit', args=[self.objectId])
	
	def redemption_count(self):
		return parse("GET", "classes/Redemption",
            query={"where":json.dumps({"Reward":self.objectId}), 
                    "count":1,"limit":0})["count"]

class Punch(ParseObject):
    """ Equivalence class of apps.rewards.models.Punch """
    def __init__(self, data={}):
        self.date_punched = data.get("date_punched", datetime.now().isoformat())
        self.punches = data.get("punches")

        self.Reward = data.get("Reward")
        self.Patron = data.get("Patron")
        self.Employee = data.get("Employee")
        
        super(Punch, self).__init__(data)

class Redemption(ParseObject):
    """ Equivalence class of apps.rewards.models.Redemption """
    def __init__(self, data={}):
        self.date_punched = data.get("date_punched", datetime.now().isoformat())
        self.punches = data.get("punches")

        self.Reward = data.get("Reward")
        self.Patron = data.get("Patron")
        self.Employee = data.get("Employee")
        
        super(Redemption, self).__init__(data)
    

