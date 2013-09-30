"""
Queries all Parse models/classes for invalid rows.
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

EMAILS = ("vandolf@repunch.com",)# "mike@repunch.com")

MODELS = (Account, Employee, Message, MessageStatus, Punch,
    RedeemReward, Store, Settings, Subscription, Invoice,
    Patron, PatronStore, PunchCode, FacebookPost)
    
    
class Command(BaseCommand):
    """
    Keeps track of abnormalities to be emailed to EMAILS.
    The format is as follows
        { 
            cls.__name__ : {
                cls.fields_required[1] : (cls.instance, ...)
            }, ...
        } 
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the abnormalities.
        """
        super(Command, self).__init__(*args, **kwargs)
        self.abnormalities = { m.__name__:{} for m in MODELS }

    def handle(self, *args, **options):
        # Loop through all of the models in MODELS
        for model in MODELS:
            fields_required = model.fields_required()
            model_class = fields_required.pop(0)
            
            if len(fields_required) == 0:
                continue
                
            for field in fields_required:
                self.process_field(model_class, field)
    
    def resolve_field(self, model_class, field):
        """
        Calls the proper handler for the given field.
        """
        field_type = type(field)
        if field_type in (str, unicode):
            self.process_str(model_class, field)
        elif field_type is tuple:
            self.process_tuple(model_class, field)
        elif field_type is list:
            self.process_list(model_class, field)
        elif field_type is dict:
            self.process_dict(model_class, field)
            
    def process_str(self, model_class, field):
        """
        Adds to abnormalities model instances that have a null value
        for the given field.
        """
        pass    
        
    def process_tuple(self, model_class, field):
        """
        Adds to abnormalities model instances that have 1 or more
        fields in the given tuple that are null if not all of them
        are null.
        """
        pass    
        
    def process_list(self, model_class, field):
        """
        Adds to abnormalities model instances that have a null value
        for all fields in the given list.
        """
        pass    
        
    def process_dict(self, model_class, field):
        """
        Adds to abnormalities model instances that do not have the
        given value for the given field.
        """
        pass    
        
       
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    
    
