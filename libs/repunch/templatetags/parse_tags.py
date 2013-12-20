"""
Template tags for the Parse backend.
"""

from django import template

from parse.apps.accounts import sub_type

register = template.Library()

@register.filter
def get_total_punches(punches):
    """ 
    Returns the total number of punches in the list of Punches.
    punches_map is a list of dicts with a key "punch"
    
    e.g. punches_map = [{
        "store_location": store_location,
        "punch": punch,
        "employee": employee,
    },...]
    """
    total = 0
    for punch in punches:
        # incase that punches was saved as a str
        total += int(punch['punch'].punches)
        
    return total
