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

from libs.dateutil.relativedelta import relativedelta
from parse.notifications import send_email_passed_user_limit
from parse.apps.accounts import sub_type

class Command(BaseCommand):
    def handle(self, *args, **options):
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
        
        ## SUB_TYPE 0
        # 1st day
        # 4th day
        # 8th day
        # 14th day
        
        
        ## SUB_TYPE 1
        # 1st day
        # 4th day
        # 8th day
        # 14th day
        
        
        
        conn.close()
