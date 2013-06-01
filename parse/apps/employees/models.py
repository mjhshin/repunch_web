"""
Parse equivalence of Django apps.employees.models
""" 

from datetime import datetime

from parse.core.models import ParseObject

class Employee(ParseObject):
    """ Equivalence class of apps.employees.models.Employee """
    PENDING = "Pending"
    APPROVED = "Approved"
    DENIED = "Denied"

    def __init__(self, **data):
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.email = data.get("email")
        self.date_added = data.get("date_added", datetime.now().isoformat())
        self.status = data.get("status", PENDING)
        self.employee_avatar = data.get("employee_avatar")

        self.Store = data.get("Store")

        super(Employee, self).__init__(False, **data)

    def lifetime_punches(self):
        return Employee.objects().count(objectId=self.objectId)
