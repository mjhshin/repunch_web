from __future__ import division
from django import template
from datetime import datetime

from parse.apps.messages.models import Message
from parse.utils import parse

register = template.Library()

@register.simple_tag
def account_user_usage(account, percent_of=None):
    store = account.get('store')
    atype = account.get('subscription').get('subscriptionType')
    
    if atype.max_users == -1:
        percent = 0
    else:
        percent = store.active_users/atype.max_users
        if(percent > 1):
            percent = 1
    
    if percent_of != None:
        return int(percent * percent_of)
    
    return percent;

@register.assignment_tag
def account_alert(account):
    store = account.get('store')
    account.get('subscription')
    atype = account.get('subscription').get('subscriptionType')
    
    # may cause division by 0!!!
    percent = store.active_users / atype.max_users
    
    #if they are at 80 percent of their users, alert
    return (percent >= .8)

@register.simple_tag
def account_message_usage(account, percent_of=None):
    atype = account.get('subscription').get('subscriptionType')
    now = datetime.now()

    # create the datetime object for comparison since all dates
    # are stored as strings
    # TODO
    
    message_count = 0 
    
    percent = message_count/atype.max_messages
    if(percent > 1): #don't go past 1
        percent = 1
    
    if percent_of != None:
        return int(percent * percent_of)
    
    return percent;

@register.simple_tag
def account_user_count(account):
    return account.store.active_users
    

@register.simple_tag
def account_message_count(account):
    
    now = datetime.now()
    # TODO
    return 0

