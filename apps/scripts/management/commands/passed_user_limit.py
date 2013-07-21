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
"""

from django.utils import timezone
from django.core import mail
from django.core.management.base import BaseCommand
import requests, json

from libs.dateutil.relativedelta import relativedelta
from parse.notifications import send_email_passed_user_limit
from parse.apps.accounts import sub_type
from parse.apps.accounts.models import Account
from repunch.settings import COMET_REQUEST_RECEIVE

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
            subscriptionType=0, limit=900, 
            date_passed_user_limit__lte=day1_end,
            date_passed_user_limit__gte=day1_start):
            # with pp_cc_id
            if sub.pp_cc_id:
                sub.subscriptionType = 1
                sub.date_passed_user_limit = None
                sub.update()
                # notify the dashboards of these changes
                payload={"updatedSubscription_one":\
                    subscription.jsonify()}
                requests.post(COMET_REQUEST_RECEIVE + sub.Store,
                    data=json.dumps(payload))
                send_email_passed_user_limit(Account.objects().get(\
                    Store=sub.Store), sub.get("store"), 
            # no pp_cc_id
            else:
        
        ## 4th day
        ## 8th day
        ## 14th day
        
        
        
        
        #### SUB_TYPE 1
        ## 1st day
        # with pp_cc_id
        
        # no pp_cc_id
        
        
        ## 4th day
        ## 8th day
        ## 14th day
        
        
        
        conn.close()
