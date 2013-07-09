"""
Some extra methods involving dates.
"""

from calendar import monthrange
from datetime import date

def start_month(d):
    """ 
    Returns the date object with the same year and month as d
    but with the day set to 1.

    Note that attributes of date objects are not writable, which is
    why this method is useful.
    """
    return date(d.year, d.month, 1)

def end_month(d):
    """ 
    Returns the date object with the same year and month as d
    but with the day set to the last day of the month.

    Note that attributes of date objects are not writable, which is
    why this method is useful.
    """
    return date(d.year, d.month, monthrange(d.year, d.month)[1])
