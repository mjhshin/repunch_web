"""
Detects suspicious activity:
    * One patron getting punched 6+ times in one day in any location (cummulative)
    * Punches being granted when the store is closed for each location
    
This scans through each store. Then for each employee, if any, scans
through all the punches given today and checks for one patron
getting punched more than 6 times and punches being granted when the 
store is closed (only if hours are provided). 

An email is sent to the store owner if there is any suspicious 
activity detected. Each email is divided into 2 chunks:

1. List of patrons that got punched more than 6 times today.
    - This is the total count for all punches in all store locations
        for this patron.

2. List of patrons that were punched when the store is closed.
    - The suspicious punches are grouped per patron.

Each chunk has the following format (both grouped by patron):
 
    Chunk format: {
                    "patron_id": {
                        "account": account,
                        "patron": patron, 
                        "punches": [{
                            "store_location": store_location,
                            "punch": punch,
                            "employee":employee
                        }],
                    },...
                 }
                 
The admins also get a copy.
    
    Chunk format: [{
                "store_acc": account, # store owner's account
                "store": store,
                "data": (chunk1, chunk2),
                },...]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core import mail
from dateutil.tz import tzutc
from smtplib import SMTPServerDisconnected
import pytz

from libs.dateutil.relativedelta import relativedelta
from parse.notifications import send_email_suspicious_activity,\
send_email_suspicious_activity_admin
from parse.apps.accounts.models import Account
from parse.apps.stores.models import Store
from parse.apps.patrons.models import Patron
from parse.apps.employees import APPROVED
from repunch.settings import DEBUG

class Command(BaseCommand):
    def handle(self, *args, **options):
        # for logging when ran by CRON
        print "Running detect_suspicious_activity: " + str(timezone.now())
    
        # first count the number of active stores
        store_count = Store.objects().count(active=True)

        end = timezone.now()
        start = end + relativedelta(hours=-24)
        conn = mail.get_connection(fail_silently=(not DEBUG))
        conn.open()
        
        # to send to the admins
        admin_chunks = []
        
        # get 500 stores at a time
        LIMIT, skip = 500, 0
        while store_count > 0:
            for store in Store.objects().filter(active=True,
                include="store_locations", 
                limit=LIMIT, skip=skip, order="createdAt"):
                ### CHUNK1 ####################################
                chunk1, account_patron, patron_punch = {}, {}, {}
                total_punches = []
                
                # check approved EMPLOYEES
                employees = store.get("employees", status=APPROVED,
                    limit=900)
                employee_punches = []
                
                def add_to_patron_punch(punch, employee=None):
                    if punch.Patron not in patron_punch:
                        patron_punch[punch.Patron] =\
                            [{"punch":punch, "employee": employee}]
                    else:
                        patron_punch[punch.Patron].append({"punch":\
                            punch, "employee":employee})
                            
                def get_location(location_id):
                    for loc in store.store_locations:
                        if loc.objectId == location_id:
                            return loc
                
                if employees and len(employees) > 0:
                    # check all the punches of each employee
                    for employee in employees:
                        # get all the punches for today
                        punches = employee.get("punches", limit=900, 
                            createdAt__lte=end, createdAt__gte=start)
                        if not punches:
                            continue
                            
                        # for querying the dashboard punches
                        employee_punches.extend([p.objectId for p in\
                            punches])
                            
                        # group the punches by patron
                        for punch in punches:
                            add_to_patron_punch(punch, employee)
                                
                # now check DASHBOARD
                punches = store.get("punches", limit=900,
                    createdAt__lte=end, createdAt__gte=start,
                    objectId__nin=employee_punches)

                # group the punches by patron
                if punches:
                    for punch in punches:
                        add_to_patron_punch(punch, None)
                
                # check for a group with a list >= 6
                for key, val in patron_punch.iteritems():
                    suspicious_punches = []
                    if val and len(val) >= 6:
                        for punch in val:
                            suspicious_punches.append({
                                "store_location":\
                                    get_location(punch["punch"].store_location_id),
                                "punch": punch["punch"],
                                "employee": punch["employee"]
                            })
                                
                        # cache the account and patron
                        if key not in account_patron:
                            acc = Account.objects().get(Patron=key, include="Patron")
                            account_patron[key] = {
                                "account": acc,
                                "patron": acc.patron,
                            }
                            
                        if key not in chunk1:
                            chunk1[key] = {
                                "account":\
                                   account_patron[key]['account'],
                                "patron":\
                                   account_patron[key]['patron'],
                                "punches": suspicious_punches
                            }
                        else:
                            chunk1[key]['punches'].extend(suspicious_punches)
                        
                        
                ### CHUNK2 ####################################
                # hours per location
                # punches are still grouped per patron
                chunk2 = {}
                for loc in store.store_locations:
                    if loc.hours and len(loc.hours) > 0 and\
                        loc.hours[0]['day'] != 0: # 24/7
                        # check for punches out of hours
                        tz = pytz.timezone(loc.store_timezone)
                        start = timezone.localtime(start, tz)
                        end = timezone.localtime(end, tz)
                        # isoweekday is from 1-7 monday to sunday
                        # convert to 1-7 sunday to saturday
                        day1_weekday = (start.isoweekday()) % 7 + 1
                        day2_weekday = (end.isoweekday()) % 7 + 1
                        # get the hours for day1 and day2
                        def get_hours_range(weekday, d):
                            for hr in loc.hours:
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
                        
                        for key, val in patron_punch.iteritems():
                            if not val:
                                continue
                                
                            suspicious_punches = []

                            # process only those punches that are in this location
                            for p in [ x for x in val if
                                x["punch"].store_location_id == loc.objectId ]:
                                punch = p["punch"]
                                # suspicious if not in hours1 and 2
                                if not (hours1_start and\
                                    punch.createdAt>hours1_start and\
                                    punch.createdAt<hours1_end) and\
                                    not (hours2_start and\
                                    punch.createdAt>hours2_start and\
                                    punch.createdAt<hours2_end):
                                    # not in hours1 or 2 so suspicious!   
                                    suspicious_punches.append({
                                        "store_location": loc,
                                        "punch":punch,
                                        "employee": p["employee"],
                                    })
                            
                            if len(suspicious_punches) == 0:
                                continue
                                
                            # cache the account and patron
                            if key not in account_patron:
                                acc = Account.objects().get(Patron=key,
                                    include="Patron")
                                account_patron[key] = {
                                    "account": acc,
                                    "patron": acc.patron,
                                }
                                
                            if key not in chunk2:
                                chunk2[key] = {
                                    "account":\
                                       account_patron[key]['account'],
                                    "patron":\
                                       account_patron[key]['patron'],
                                    "punches": suspicious_punches
                                }
                            else:
                                chunk2[key]['punches'].extend(suspicious_punches)
                    
                # all tasks are done for this store - send email
                if len(chunk1) > 0 or len(chunk2) > 0:
                    store_acc = Account.objects().get(Store=store.objectId)
                    admin_chunks.append({
                        "store_acc": store_acc,
                        "store": store,
                        "data": (chunk1, chunk2),
                    })
                    
                    try:
                        send_email_suspicious_activity(store_acc,
                            store, chunk1, chunk2, conn)
                    except SMTPServerDisconnected:
                        conn = mail.get_connection(fail_silently=(not DEBUG))
                        conn.open()
                        send_email_suspicious_activity(store_acc,
                            store, chunk1, chunk2, conn)
                        
            # end of while loop
            store_count -= LIMIT
            skip += LIMIT
            
        #if len(admin_chunks) > 0: TODO
        #   send_email_suspicious_activity_admin(admin_chunks, start, end, conn)
        
        # everything is done. close the connection
        try:
            conn.close()
        except Exception:
            pass 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
