"""
Template tags for the Parse backend.
"""

from django import template

from parse.apps.accounts import sub_type

register = template.Library()

@register.filter
def get_total_punches(punches_map):
    """ 
    Returns the total number of punches in the list of Punches.
    punches_map is a list of dicts with a key "punch"
    
    e.g. punches_map = {
        "store_location_id":\
            [{"store_location": store_location,
                "punch":punch, "employee":employee}], ...
    }
    """
    total = 0
    for lst in punches_map.itervalues():
        for p_map in lst:
            # incase that punches was saved as a str
            total += int(p_map['punch'].punches)
        
    return total
