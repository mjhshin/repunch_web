"""
This script scans through all active stores that have reached their 
user limit. If a store has reached their user limit, then the store
owner is sent an email notification with the date in which the
associated account will be disabled only if their credit card info
is not yet provided. If, however, we already have their credit card
info, we attempt to upgrade their account and simply send them a 
notification. 

Email send flow: now, 4 days, 8 days, 12 days
Account disabled: 14th day from now

NOTE that this does not detect date_passed_user_limit!
It must be set somewhere else (comet view)
"""

from django.utils import timezone
from django.core import mail
from django.core.management.base import BaseCommand
import requests, json

from libs.dateutil.relativedelta import relativedelta
from parse.notifications import send_email_passed_user_limit
from parse.apps.accounts import sub_type
from parse.apps.accounts.models import Account
from parse.apps.stores.models import Subscription
from repunch.settings import COMET_REQUEST_RECEIVE,\
USER_LIMIT_PASSED_DISABLE_DAYS, DEBUG, COMET_RECEIVE_KEY_NAME,\
COMET_RECEIVE_KEY

class Command(BaseCommand):
    def handle(self, *args, **options):
        # TODO there is a limit of 900 on queries
        
        conn = mail.get_connection(fail_silently=(not DEBUG))
        conn.open()
        now = timezone.now()
        # 1st day time range
        day1_end = now.replace()
        day1_start = day1_end + relativedelta(hours=-24)
        # 4th day time range
        day4_end = now + relativedelta(days=-4)
        day4_start = day4_end + relativedelta(hours=-24)
        # 8th day time range
        day8_end = now + relativedelta(days=-8)
        day8_start = day8_end + relativedelta(hours=-24)
        # 14th day time range
        day14_end = now + relativedelta(days=-14)
        day14_start = day14_end + relativedelta(hours=-24)
        
        #### SUB_TYPE 0
        ## 1st day
        for sub in Subscription.objects().filter(\
            subscriptionType=0, limit=900, include="Store", 
            date_passed_user_limit__lte=day1_end,
            date_passed_user_limit__gte=day1_start):
            # with pp_cc_id
            if sub.pp_cc_id and len(sub.pp_cc_id) > 0:
                sub.subscriptionType = 1
                sub.date_passed_user_limit = None
                sub.update()
                # notify the dashboards of these changes
                payload={
                    COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                    "updatedSubscription_one": sub.jsonify()
                }
                requests.post(COMET_REQUEST_RECEIVE + sub.Store,
                    data=json.dumps(payload), verify=False)
                package = {
                    "status": "upgraded",
                    "sub_type": sub_type[0]["name"],
                    "new_sub_type": sub_type[1]["name"],
                    "new_sub_type_cost": sub_type[1]["monthly_cost"],
                    "new_max_patronStore_count":\
                        sub_type[1]["max_users"], 
                    "patronStore_count": sub.store.get(\
                        "patronStores", limit=0, count=1),
                }
                send_email_passed_user_limit(Account.objects().get(\
                    Store=sub.Store), sub.store, package, conn)
            # no pp_cc_id
            else:
                package = {
                    "sub_type": sub_type[0]["name"],
                    "max_patronStore_count": sub_type[0]["max_users"],
                    "patronStore_count": sub.store.get(\
                        "patronStores", limit=0, count=1),
                    "disable_date": sub.date_passed_user_limit + 
                        relativedelta(days=\
                            USER_LIMIT_PASSED_DISABLE_DAYS),
                }
                send_email_passed_user_limit(Account.objects().get(\
                    Store=sub.Store), sub.store, package, conn)
        
        ## 4th day
        for sub in Subscription.objects().filter(\
            subscriptionType=0, limit=900, include="Store", 
            date_passed_user_limit__lte=day4_end,
            date_passed_user_limit__gte=day4_start):
            package = {
                "sub_type": sub_type[0]["name"],
                "max_patronStore_count": sub_type[0]["max_users"],
                "patronStore_count": sub.store.get(\
                    "patronStores", limit=0, count=1),
                "disable_date": sub.date_passed_user_limit + 
                    relativedelta(days=\
                        USER_LIMIT_PASSED_DISABLE_DAYS),
            }
            send_email_passed_user_limit(Account.objects().get(\
                Store=sub.Store), sub.store, package, conn)
        ## 8th day
        for sub in Subscription.objects().filter(\
            subscriptionType=0, limit=900, include="Store", 
            date_passed_user_limit__lte=day8_end,
            date_passed_user_limit__gte=day8_start):
            package = {
                "sub_type": sub_type[0]["name"],
                "max_patronStore_count": sub_type[0]["max_users"],
                "patronStore_count": sub.store.get(\
                    "patronStores", limit=0, count=1),
                "disable_date": sub.date_passed_user_limit + 
                    relativedelta(days=\
                        USER_LIMIT_PASSED_DISABLE_DAYS),
            }
            send_email_passed_user_limit(Account.objects().get(\
                Store=sub.Store), sub.store, package, conn)
        ## 14th day
        for sub in Subscription.objects().filter(\
            subscriptionType=0, limit=900, include="Store", 
            date_passed_user_limit__lte=day14_end,
            date_passed_user_limit__gte=day14_start):
            package = { "status": "disabled" }
            send_email_passed_user_limit(Account.objects().get(\
                Store=sub.Store), sub.store, package, conn)
        
        
        
        #### SUB_TYPE 1
        ## 1st day
        for sub in Subscription.objects().filter(\
            subscriptionType=1, limit=900, include="Store", 
            date_passed_user_limit__lte=day1_end,
            date_passed_user_limit__gte=day1_start):
            # with pp_cc_id
            if sub.pp_cc_id and len(sub.pp_cc_id) > 0:
                sub.subscriptionType = 2
                sub.date_passed_user_limit = None
                sub.update()
                # notify the dashboards of these changes
                payload={
                    COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                    "updatedSubscription_one": sub.jsonify()
                }
                requests.post(COMET_REQUEST_RECEIVE + sub.Store,
                    data=json.dumps(payload), verify=False)
                package = {
                    "status": "upgraded",
                    "sub_type": sub_type[1]["name"],
                    "new_sub_type": sub_type[2]["name"],
                    "new_sub_type_cost": sub_type[2]["monthly_cost"],
                    "new_max_patronStore_count": "UNLIMITED",
                    "patronStore_count": sub.store.get(\
                        "patronStores", limit=0, count=1),
                }
                send_email_passed_user_limit(Account.objects().get(\
                    Store=sub.Store), sub.store, package, conn)
            # no pp_cc_id
            else:
                package = {
                    "sub_type": sub_type[1]["name"],
                    "max_patronStore_count": sub_type[1]["max_users"],
                    "patronStore_count": sub.store.get(\
                        "patronStores", limit=0, count=1),
                    "disable_date": sub.date_passed_user_limit + 
                        relativedelta(days=\
                            USER_LIMIT_PASSED_DISABLE_DAYS),
                }
                send_email_passed_user_limit(Account.objects().get(\
                    Store=sub.Store), sub.store, package, conn)
        
        ## 4th day
        for sub in Subscription.objects().filter(\
            subscriptionType=1, limit=900, include="Store", 
            date_passed_user_limit__lte=day4_end,
            date_passed_user_limit__gte=day4_start):
            package = {
                "sub_type": sub_type[1]["name"],
                "max_patronStore_count": sub_type[1]["max_users"],
                "patronStore_count": sub.store.get(\
                    "patronStores", limit=0, count=1),
                "disable_date": sub.date_passed_user_limit + 
                    relativedelta(days=\
                        USER_LIMIT_PASSED_DISABLE_DAYS),
            }
            send_email_passed_user_limit(Account.objects().get(\
                Store=sub.Store), sub.store, package, conn)
        ## 8th day
        for sub in Subscription.objects().filter(\
            subscriptionType=1, limit=900, include="Store", 
            date_passed_user_limit__lte=day8_end,
            date_passed_user_limit__gte=day8_start):
            package = {
                "sub_type": sub_type[1]["name"],
                "max_patronStore_count": sub_type[1]["max_users"],
                "patronStore_count": sub.store.get(\
                    "patronStores", limit=0, count=1),
                "disable_date": sub.date_passed_user_limit + 
                    relativedelta(days=\
                        USER_LIMIT_PASSED_DISABLE_DAYS),
            }
            send_email_passed_user_limit(Account.objects().get(\
                Store=sub.Store), sub.store, package, conn)
        ## 14th day
        for sub in Subscription.objects().filter(\
            subscriptionType=1, limit=900, include="Store", 
            date_passed_user_limit__lte=day14_end,
            date_passed_user_limit__gte=day14_start):
            package = { "status": "disabled" }
            send_email_passed_user_limit(Account.objects().get(\
                Store=sub.Store), sub.store, package, conn)
        
        
        
        conn.close()
