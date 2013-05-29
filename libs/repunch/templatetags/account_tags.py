from __future__ import division
from django import template
import datetime

from apps.messages.models import Message

register = template.Library()

@register.simple_tag
def account_user_usage(account, percent_of=None):
    
    return 0

@register.assignment_tag
def account_alert(account):
    return False

@register.simple_tag
def account_message_usage(account, percent_of=None):
    return 0

@register.simple_tag
def account_user_count(account):
    return 0

@register.simple_tag
def account_message_count(account):
    return 0

