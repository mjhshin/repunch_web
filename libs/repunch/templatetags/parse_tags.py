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
