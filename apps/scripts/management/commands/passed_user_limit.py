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
from django.core.management.base import BaseCommand

from parse.notifications import 
from parse.apps.accounts import sub_type

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
