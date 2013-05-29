"""
Parse equivalence of Django apps.employees.models
""" 

from datetime import date

from parse.core.models import ParseObject
from parse.utils import parse

class Employee(ParseObject):
    """ Equivalence class of apps.employees.models.Employee """
    PENDING = "Pending"
    APPROVED = "Approved"
    DENIED = "Denied"

    def __init__(self, data={}):
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.email = data.get("email")
        self.date_added = data.get("date_added", date.today())
        self.status = data.get("status", PENDING)
        self.employee_avatar = data.get("employee_avatar")

        self.Store = data.get("Store")      
        self.store = None

        super(Employee, self).__init__(data)

    def lifetime_punches(self):
        return parse("GET", "classes/Punch", query={"where":json.dumps({
               "Employee":self.objectId}),"count":1,"limit":0})["count"]
