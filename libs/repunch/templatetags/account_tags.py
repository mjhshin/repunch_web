from __future__ import division
from django import template
from datetime import date
from dateutil import parser

from libs.dateutil.extras import start_month, end_month
from parse.utils import parse
from parse.apps.accounts import sub_type

register = template.Library()

@register.simple_tag
def account_user_usage(session, percent_of=None):
    account = session.get('account')
    store = account.get('store')
    atype = sub_type[store.get('subscription').get('subscriptionType')]
    num_patrons = store.get('patronStores', count=1, limit=0)
    
    if atype['max_users'] == -1:
        percent = 0
    else:
        # may cause division by 0!!!
        percent = num_patrons / atype['max_users']
        if(percent > 1):
            percent = 1
    
    if percent_of != None:
        return int(percent * percent_of)
        
    account.set('store', store)
    session['account'] = account
    
    return percent;

@register.assignment_tag
def account_alert(session):
    account = session.get('account')
    store = account.get('store')
    atype = sub_type[store.get('subscription').get('subscriptionType')]
    num_patrons = store.get('patronStores', count=1, limit=0)
    # may cause division by 0!!!
    percent = num_patrons / atype['max_users']
    
    account.set('store', store)
    session['account'] = account
    
    #if they are at 80 percent of their users, alert
    return (percent >= .8)

@register.simple_tag
def account_message_usage(account, percent_of=None):
    atype = sub_type[account.get('store').get('subscription').get('subscriptionType')]
    
    today = date.today()
    message_count = account.get("store").get('sentMessages', 
            createdAt__gte=start_month(today),
            createdAt__lte=end_month(today),
            count=1, limit=0)
    
    percent = message_count/atype['max_messages']
    if(percent > 1): #don't go past 1
        percent = 1
    
    if percent_of != None:
        return int(percent * percent_of)
    
    return percent;

@register.simple_tag
def account_user_count(account):
    return account.get('store').get('patronStores', 
            count=1, limit=0)
    

@register.simple_tag
def account_message_count(account):
    today = date.today()
    return account.get("store").get('sentMessages', 
            createdAt__gte=start_month(today),
            createdAt__lte=end_month(today),
            count=1, limit=0)

