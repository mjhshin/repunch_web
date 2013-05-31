"""
Template tags for the Parse backend.
"""

from django import template

register = template.Library()

@register.filter
def get(parseObject, attr):
    """
    This simply calls the get method of the parseObject with the
    parameter attr.
    """
    return parseObject.get(attr)

    
