from django import template
from datetime import date, timedelta, datetime
import time

register = template.Library()

@register.simple_tag
def today(add_days=0):
    d = date.today()
    if add_days != 0:
        d = d+timedelta(days=add_days)
    return d.strftime("%m/%d/%Y")


@register.simple_tag
def timestamp():
    return time.mktime(time.gmtime())