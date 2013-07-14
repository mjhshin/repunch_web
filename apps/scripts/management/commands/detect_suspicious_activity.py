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
from dateutil.tz import tzutc
import pytz

from libs.dateutil.relativedelta import relativedelta
from parse.notifications import send_email_suspicious_activity
from parse.apps.accounts.models import Account
from parse.apps.stores.models import Store
from parse.apps.patrons.models import Patron
from parse.apps.employees import APPROVED
from repunch.settings import DEBUG

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
                limit=900):
                ### CHUNK1 ####################################
                chunk1, account_patron, patron_punch = [], {}, {}
                total_punches = []
                # check approved EMPLOYEES
                employees = store.get("employees", status=APPROVED,
                    limit=900)
                if employees and len(employees) > 0:
                    # check all the punches of each employee
                    for employee in employees:
                        # get all the punches for today
                        punches = employee.get("punches", limit=900, 
                            createdAt__lte=end, createdAt__gte=start)
                        if not punches:
                            continue
                        # cache the punches
                        total_punches.append({"punches":punches,
                            "employee":employee})
                        # group the punches by patron
                        for punch in punches:
                            if punch.Patron not in patron_punch:
                                patron_punch[punch.Patron] =\
                                    [{"punch":punch, "employee":\
                                        employee}]
                            else:
                                patron_punch[\
                                    punch.Patron].append({"punch":\
                                        punch, "employee":employee})
                                
                # now check DASHBOARD
                employee_punches = []
                for pe in total_punches:
                    employee_punches.extend([p.objectId for p in\
                    pe["punches"]])
                punches = store.get("punches", limit=900,
                    createdAt__lte=end, createdAt__gte=start,
                    objectId__nin=employee_punches)
                # cache the punches
                total_punches.append({"punches":punches,
                            "employee":None})
                # group the punches by patron
                if punches:
                    for punch in punches:
                        if punch.Patron not in patron_punch:
                            patron_punch[punch.Patron] =\
                                [{"punch":punch, "employee": None}]
                        else:
                            patron_punch[punch.Patron].append(\
                                {"punch":punch, "employee":None})
                # patron_punch now has all of the punches grouped!
                
                # check for a group with a list >= 6
                for key, val in patron_punch.iteritems():
                    suspicious_punch_list = []
                    if val and len(val) >= 6:
                        for punch in val:
                            suspicious_punch_list.append({
                                "punch":punch["punch"],
                                "employee": punch["employee"]
                            })
                                
                        # cache the account and patron
                        if key not in account_patron:
                            account_patron[key] = {
                                "account":\
                                Account.objects().get(\
                                    Patron=key),
                                "patron":\
                                    Patron.objects().get(objectId=key)
                            }
                        chunk1.append({
                            "account":\
                               account_patron[key]['account'],
                            "patron":\
                               account_patron[key]['patron'],
                            "punches": suspicious_punch_list
                        })
                        
                        
                ### CHUNK2 ####################################
                chunk2, hours = [], store.hours
                if hours or len(hours) > 0:
                    # check for punches out of hours
                    tz = pytz.timezone(store.store_timezone)
                    start = timezone.localtime(start, tz)
                    end = timezone.localtime(end, tz)
                    # get the 2 full days
                    day1_start =\
                        start.replace(hour=0, minute=0, second=0)
                    day1_end =\
                       start.replace(hour=23, minute=59, second=59)
                    day2_start =\
                        end.replace(hour=0, minute=0, second=0)
                    day2_end =\
                        end.replace(hour=23, minute=59, second=59)
                    # isoweekday is from 1-7 monday to sunday
                    # convert to 1-7 sunday to saturday
                    day1_weekday = (start.isoweekday()) % 7 + 1
                    day2_weekday = (end.isoweekday()) % 7 + 1
                    # get the hours for day1 and day2
                    def get_hours_range(weekday, d):
                        for hr in hours:
                            if hr["day"] == weekday:
                                hr_start_hour =\
                                    int(hr["open_time"][:2])
                                hr_start_minute =\
                                    int(hr["open_time"][2:])
                                hr_end_hour =\
                                    int(hr["close_time"][:2])
                                hr_end_minute =\
                                    int(hr["close_time"][2:])
                                return d.replace(hour=hr_start_hour,
                                    minute=hr_start_minute),\
                                    d.replace(hour=hr_end_hour,
                                    minute=hr_end_minute)
                        return None, None
                    
                    (hours1_start, hours1_end) =\
                        get_hours_range(day1_weekday, start)
                    (hours2_start, hours2_end) =\
                        get_hours_range(day2_weekday, end)
                        
                    # now convert to utc since punch times are in utc
                    if hours1_start:
                        hours1_start =\
                            timezone.localtime(hours1_start, tzutc())
                        hours1_end =\
                            timezone.localtime(hours1_end, tzutc())
                    if hours2_start:
                        hours2_start =\
                            timezone.localtime(hours2_start, tzutc())
                        hours2_end =\
                            timezone.localtime(hours2_end, tzutc())
                    
                    if hours1_start or hours2_start:
                        for key, val in patron_punch.iteritems():
                            if not val:
                                continue
                                
                            suspicious_punch_list = []
                            for punch in val:
                                # not suspicious if in hours1 or 2
                                if (hours1_start and\
                                    punch.createdAt>hours1_start and\
                                    punch.createdAt<hours1_end) or\
                                    (hours2_start and\
                                    punch.createdAt>hours2_start and\
                                    punch.createdAt<hours2_end):
                                    continue
                                # not in hours1 or 2 so suspicious!   
                                suspicious_punch_list.append({
                                    "punch":punch["punch"],
                                    "employee": punch["employee"]
                                })
                            
                            if len(suspicious_punch_list) == 0:
                                continue
                                
                            # cache the account and patron
                            if key not in account_patron:
                                account_patron[key] = {
                                    "account":\
                                        Account.objects().get(\
                                            Patron=key),
                                    "patron":\
                                        Patron.objects().get(\
                                            objectId=key)
                                }
                            chunk2.append({
                                "account":\
                                   account_patron[key]['account'],
                                "patron":\
                                   account_patron[key]['patron'],
                                "punches": suspicious_punch_list
                            })
                
                if len(chunk1) > 0 or len(chunk2) > 0:
                    send_email_suspicious_activity(\
                        Account.objects().get(Store=store.objectId),
                        store, chunk1, chunk2, start, end, conn)
        
        # else retrieve them in chunks ordered by createdAt TODO
        conn.close()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
