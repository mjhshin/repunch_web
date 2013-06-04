from __future__ import division
from django import template
from datetime import date
from dateutil import parser

from libs.dateutil.extras import start_month, end_month
from parse.apps.messages.models import Message
from parse.utils import parse
from parse.apps.accounts import sub_type

register = template.Library()

@register.simple_tag
def account_user_usage(account, percent_of=None):
    store = account.get('store')
    atype = sub_type[account.get('subscription').get('subscriptionType')]
    
    if atype['max_users'] == -1:
        percent = 0
    else:
        percent = store.active_users/atype['max_users']
        if(percent > 1):
            percent = 1
    
    if percent_of != None:
        return int(percent * percent_of)
    
    return percent;

@register.assignment_tag
def account_alert(account):
    store = account.get('store')
    account.get('subscription')
    atype = sub_type[account.get('subscription').get('subscriptionType')]
    
    # may cause division by 0!!!
    percent = store.active_users / atype['max_users']
    
    #if they are at 80 percent of their users, alert
    return (percent >= .8)

@register.simple_tag
def account_message_usage(account, percent_of=None):
    atype = sub_type[account.get('subscription').get('subscriptionType')]
    
    today = date.today()
    message_count = Message.objects().count(Store=\
            account.get("Store"), date_sent__gte=start_month(today),
            date_sent__lte=end_month(today))
    
    percent = message_count/atype['max_messages']
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
    today = date.today()
    return Message.objects().count(Store=\
            account.get("Store"), date_sent__gte=start_month(today),
            date_sent__lte=end_month(today))

