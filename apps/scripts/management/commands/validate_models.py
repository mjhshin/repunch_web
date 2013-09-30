"""
Queries all Parse models/classes for invalid columns.
--------------------------------------------------------

# Check for null columns
--------------------------
Uses ParseObject.fields_required to get the list of Parse columns
that cannot be null. A parse query is made for each element in the 
list to see if it is null. The object(s) that have null columns,
which are not supposed to be null are then added to NULL_COLUMNS.

"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass    
    
    
    
    
