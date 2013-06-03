"""
Parse equivalence of Django apps.employees.models
""" 

from importlib import import_module

from parse.core.models import ParseObject
from parse.apps.employees import PENDING
from parse.apps.rewards.models import Punch

class Employee(ParseObject):
    """ Equivalence class of apps.employees.models.Employee """

    def __init__(self, **data):
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.email = data.get("email")
        self.status = data.get("status", PENDING)
        self.employee_avatar = data.get("employee_avatar")
        # must be updated everytime a punch event occurs TODO
        self.lifetime_punches = data.get("lifetime_punches", 0)

        self.Store = data.get("Store")

        super(Employee, self).__init__(False, **data)
    
    def get_class(self, className):
        if className == "Store":
            return getattr(import_module('parse.apps.stores.models'),
                                className)
        
