from __future__ import division
from django import template
import datetime

from apps.messages.models import Message

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
    print account.__dict__
    atype = account.get('subscription').get('subscriptionType')
    
    # may cause division by 0!!!
    percent = store.active_users / atype.max_users
    
    #if they are at 80 percent of their users, alert
    return (percent >= .8)

@register.simple_tag
def account_message_usage(account, percent_of=None):
    atype = account.get('subscription').get('subscriptionType')
    now = datetime.datetime.now()
    
    message_count = Message.objects.filter(date_sent__year=now.year, date_sent__month=now.month, store=account.get('store') ).count()    
    
    percent = message_count/atype.max_messages
    if(percent > 1): #don't go past 1
        percent = 1
    
    if percent_of != None:
        return int(percent * percent_of)
    
    return percent;

@register.simple_tag
def account_user_count(account):
    return account.get('store').active_users
    

@register.simple_tag
def account_message_count(account):
    
    now = datetime.datetime.now()
    
    return Message.objects.filter(date_sent__year=now.year, date_sent__month=now.month, store=account.get('store') ).count()

