"""
Detects suspicious activity:
    * One patron getting punched 6+ times in one day
    * Punches being granted when the store is closed
    
This scans through each store. Then for each employee, if any, scans
through all the punches given today and checks for one patron
getting punched more than 6 times AND punches being granted when the 
store is closed (only if hours are provided). 
After accumulating all the punches given by all the employees, scans
the punches given out from the dashboard and checks the same thing.

An email is sent to the store owner if there is any suspicious 
activity detected. Each email is divided into 2 chunks:

List of patrons that got punched more than 6 times today:
List of patrons that were punched when the store is closed:
    1. patron name
        * patron email
        * X punches received
            - time of punch
            - # of punches received
            - punch came from dashboard or employee
                if from employee:
                + employee name
 
    Dict format: {
                    "account": account,
                    "patron": patron, 
                    "punches": [{"punch":punch, "employee":employee}]
                 }
    
"""

from django.core.management.base import BaseCommand

from libs.dateutil.relativedelta import relativedelta
from parse.notifications import send_email_suspicious_activity

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
