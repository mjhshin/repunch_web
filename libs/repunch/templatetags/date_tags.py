
from django import template
from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from parse import session as SESSION

register = template.Library()

@register.filter
def make_aware(date, session):
    """
    Returns an aware datetime object
    """
    return timezone.make_aware(date,
        SESSION.get_store_timezone(session))
