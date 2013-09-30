"""
Queries all Parse models/classes for invalid columns.
--------------------------------------------------------

# Check for null columns & other conditions
--------------------------
Uses ParseObject.fields_required to get the list of Parse columns
that cannot be null. A parse query is made for each element in the 
list to see if it is null or does not meet a specific condition.
See ParseObject.fields_required for full documentation.
"""

from django.core.management.base import BaseCommand

from parse.apps.accounts.models import Account
from parse.apps.employees.models import Employee
from parse.apps.messages.models import Message, MessageStatus
from parse.apps.rewards.models import Punch, RedeemReward
from parse.apps.stores.models import Store, Settings, Subscription, Invoice
from parse.apps.patrons.models import Patron, PatronStore, PunchCode, FacebookPost

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
    
    
    
    
