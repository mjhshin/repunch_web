"""
Template tags for the Parse backend.
"""

from django import template

from parse.apps.accounts import sub_type

register = template.Library()

@register.filter
def get(parseObject, attr):
    """
    This simply calls the get method of the parseObject with the
    parameter attr.
    """
    if parseObject: # prevent server error
        return parseObject.get(attr)

    
@register.filter
def get_sub_type(level):
    """ returns the sub dict corresponding to the level """
    return sub_type[level]
    
    
@register.filter
def get_total_punches(punches_map):
    """ 
    Returns the total number of punches in the list of Punches.
    punches_map is a list of dicts with a key "punch"
    
    e.g. punches_map = [{
        "punch": PunchObject, ...
    }, ...]
    """
    total = 0
    for p_map in punches_map:
        # incase that punches was saved as a str- which should never b
        total += int(p_map['punch'].punches)
    return total
