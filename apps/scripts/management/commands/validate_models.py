"""
Queries all Parse models/classes for invalid rows.
--------------------------------------------------------

# Check for null columns & other conditions
-----------------------------------------------------
Uses ParseObject.fields_required to get the list of Parse columns
that cannot be null. A parse query is made for each element in the 
list to see if it is null or does not meet a specific condition.
See ParseObject.fields_required for full documentation.
"""

from django.core.management.base import BaseCommand

from parse.notifications import send_email_validate_models
from parse.apps.accounts.models import Account
from parse.apps.employees.models import Employee
from parse.apps.messages.models import Message, MessageStatus
from parse.apps.rewards.models import Punch, RedeemReward
from parse.apps.stores.models import Store, Settings, Subscription, Invoice
from parse.apps.patrons.models import Patron, PatronStore, PunchCode, FacebookPost

EMAILS = ("vandolf@repunch.com", "mike@repunch.com")

MODELS = (Account, Employee, Message, MessageStatus, Punch,
    RedeemReward, Store, Settings, Subscription, Invoice,
    Patron, PatronStore, PunchCode, FacebookPost)
    
class Command(BaseCommand):
    """
    Keeps track of abnormalities to be emailed to EMAILS.
    The format is as follows
        { 
            cls.__name__ : {
                cls.fields_required[1] : (cls.instance, ...), ...
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
            
            model_class = fields_required[0]
            fields_required = fields_required[1:]
            
            if len(fields_required) == 0:
                continue
                
            for field in fields_required:
                self.process_field(model_class, field)
                
        # send the results
        send_email_validate_models(self.abnormalities, EMAILS)
    
    def process_field(self, model_class, field):
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
            
    def add_to_abnormalities(self, model_class, field, field_abs):
        if len(field_abs) > 0:
            self.abnormalities[model_class.__name__][field] =\
                tuple(field_abs)
            
    def process_str(self, model_class, field):
        """
        Adds to abnormalities model instances that have a null value
        for the given field.
        """
        self.add_to_abnormalities(model_class, field,
            model_class.objects().filter(**{field:None}))
        
    def process_tuple(self, model_class, fields):
        """
        Adds to abnormalities model instances that have 1 or more
        fields in the given tuple that are null if not all of them
        are null.
        
        If a dict is inside a tuple then all fields in the tuple must
        not be null and the dict must be True.
        
        Nested list/tuple will not be processed.
        """
        strs = [f for f in fields if type(f) in (str, unicode)]
        dicts = [f for f in fields if type(f) is dict]
        
        # look for instances whose fields in the given fields are not
        # all null but have 1 or more (but not all) null fields.
        if len(dicts) == 0:
            for i, s in enumerate(strs):
                # all current str is null except for the current 1
                # note that this method may not produce correct
                # results if len(strs) > 2
                filter_params = {y:None for x,y in\
                    enumerate(strs) if i != x}
                filter_params.update({s + "__ne":None})
                
                # yes the key is strs
                self.add_to_abnormalities(model_class, tuple(strs),
                    model_class.objects().filter(**filter_params))
                
        else: # all strs are required here
            filter_params = {s:None for s in strs}
            
            # set the key for the abnormalities dict
            key = strs[:]
            
            for dic in dicts:
                filter_params.update(dic)
                for k in dic.iterkeys():
                    key.append(k)

            self.add_to_abnormalities(model_class, tuple(key),
                model_class.objects().filter(**filter_params))
        
    def process_list(self, model_class, fields):
        """
        Adds to abnormalities model instances that have a null value
        for all fields in the given list.
        
        This will not process anything other than strings.
        """
        self.add_to_abnormalities(model_class, tuple(fields),
            model_class.objects().filter(**{f:None for f in fields}))
        
       
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    
    
