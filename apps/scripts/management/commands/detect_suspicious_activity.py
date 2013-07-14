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
from django.utils import timezone
from django.core import mail
import pytz

from libs.dateutil.relativedelta import relativedelta
from parse.notifications import send_email_suspicious_activity
from parse.apps.accounts.models import Account
from parse.apps.stores.models import Store
from parse.apps.employees import APPROVED

class Command(BaseCommand):
    def handle(self, *args, **options):
        # first count the number of active stores
        store_count = Store.objects().count(active=True)
        end = timezone.now()
        start = end + relativedelta(hours=-24)
        conn = mail.get_connection(fail_silently=(not DEBUG))
        conn.open()
        
        # if there are less than 900 stores proceed
        if store_count < 900:
            for store in Store.objects().filter(active=True, 
                limit=900)
                ### CHUNK1 ####################################
                chunk1, account_patron = {}, {}
                employee_punches = []
                # check approved EMPLOYEES
                employees = store.get("employees", status=APPROVED,
                    limit=900)
                if len(employees) > 0:
                    # check all the punches of each employee
                    for employee in employees:
                        # get all the punches for today
                        punches = employee.get("punches", limit=900, 
                            createdAt__lte=end, createdAt__gte=start)
                        if not punches:
                            break
                        # record the punches for store query
                        employee_punches.extend(\
                            [p.objectId for p in punches])
                        # group the punches by patron
                        patron_punch = {}
                        for punch in punches:
                            if punch.Patron not in patron_punch:
                                patron_punch[punch.Patron] = [punch]
                            else:
                                patron_punch[\
                                    punch.Patron].append(punch)
                        # check for a group with a list >= 6
                        suspicious_punch_list = []
                        for key, val in patron_punch.iteritems():
                            if len(val) >= 6:
                                for punch in val:
                                    suspicious_punch_list.append({
                                        "punch":punch,
                                        "employee":employee,
                                    })
                                # cache the account and patron
                                if key not in account_patron:
                                    account_patron[key] = {
                                        "account":\
                                        Account.objects().get(\
                                            Patron=key),
                                        "patron":\
                                        suspicious_punch_list[0].get(\
                                            "patron")
                                    }
                                chunk1.update({
                                    "account":\
                                       account_patron[key]['account'],
                                    "patron":\
                                       account_patron[key]['patron'],
                                    "punches": suspicious_punch_list
                                })
                                
                # now check DASHBOARD
                punches = store.get("punches", limit=900,
                    createdAt__lte=end, createdAt__gte=start,
                    objectId__nin=employee_punches)
                # group the punches by patron
                patron_punch = {}
                for punch in punches:
                    if punch.Patron not in patron_punch:
                        patron_punch[punch.Patron] = [punch]
                    else:
                        patron_punch[\
                            punch.Patron].append(punch)
                # check for a group with a list >= 6
                suspicious_punch_list = []
                for key, val in patron_punch.iteritems():
                    if len(val) >= 6:
                        for punch in val:
                            suspicious_punch_list.append({
                                "punch":punch,
                            })
                        # cache the account and patron
                        if key not in account_patron:
                            account_patron[key] = {
                                "account":\
                                Account.objects().get(\
                                    Patron=key),
                                "patron":\
                                suspicious_punch_list[0].get(\
                                    "patron")
                            }
                        chunk1.update({
                            "account":\
                               account_patron[key]['account'],
                            "patron":\
                               account_patron[key]['patron'],
                            "punches": suspicious_punch_list
                        })
                        
                        
                ### CHUNK2 ####################################
                # TODO
                chunk2 = {}
                employee_punches = []
                
                
                send_email_suspicious_activity(store, chunk1, chunk2,
                    start, end, conn)
        
        # else retrieve them in chunks ordered by createdAt TODO
        conn.close()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
