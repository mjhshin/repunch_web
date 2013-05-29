from django import template
from apps.messages.models import Feedback
from apps.employees.models import Employee
from apps.stores.models import Hours
from apps.stores import models
from libs.repunch.rphours_util import HoursInterpreter
import datetime

register = template.Library()

@register.assignment_tag
def feedback_unread(store):
    return 0


@register.assignment_tag
def employees_pending(store):
    return 0


@register.simple_tag
def hours(store):
    return "HELLO"


@register.simple_tag
def time_selector(fieldid, timestamp):
    
    return "HELLO"
