
from django import template
from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from parse import session as S

register = template.Library()

@register.filter
def make_aware(date, session):
    """
    Returns an aware datetime object
    """
    return timezone.make_aware(date, S.get_store_timezone(session))
