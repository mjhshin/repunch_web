from __future__ import division
from django import template
from dateutil import parser
from datetime import datetime

from parse.utils import parse
from parse.apps.accounts import sub_type, UNLIMITED
from parse.apps.accounts.models import Account
from parse import session as SESSION

register = template.Library()

@register.simple_tag
def account_user_usage(session, percent_of=None):
    atype = sub_type[SESSION.get_subscription(\
                session).get('subscriptionType')]
        
    num_patrons = SESSION.get_patronStore_count(session)
    
    if atype['max_users'] == UNLIMITED:
        percent = 0
    else:
        # may cause division by 0!!!
        percent = float(num_patrons) / float(atype['max_users'])
        if(percent > 1.0):
            percent = 1.0
    
    if percent_of != None:
        return int(percent * percent_of)
            
    return percent

@register.assignment_tag
def account_alert_users(session):
    subscription = SESSION.get_subscription(session)
    atype = sub_type[subscription.get('subscriptionType')]
    
    num_patrons = SESSION.get_patronStore_count(session)
    
    if atype['max_users'] == UNLIMITED:
        percent = 0
    else:
        # may cause division by 0!!!
        percent = float(num_patrons) / float(atype['max_users'])
        if(percent > 1.0):
            percent = 1.0
    
    #if they are at 80 percent of their users, alert
    if percent >= 1.0 or subscription.date_passed_user_limit:
        return 2
    elif percent >= .8:
        return 1
    return 0
    
@register.assignment_tag
def account_alert_billing(session):
    sub = SESSION.get_subscription(session)
    if sub.get('subscriptionType') != 0 and\
        sub.date_charge_failed:
        return True
        
    return False

@register.assignment_tag
def account_is_admin(session):
    return SESSION.get_store(session).is_admin(session['account'])
    
@register.assignment_tag
def employee_is_owner(session, employee_id):
    account = Account.objects().get(Employee=employee_id)
    return SESSION.get_store(session).is_owner(account)
        
@register.simple_tag
def account_message_usage(session, percent_of=None):
    atype = sub_type[SESSION.get_subscription(\
                session).get('subscriptionType')]
    
    message_count = SESSION.get_message_count(session)
    
    percent = message_count/atype['max_messages']
    if(percent > 1): #don't go past 1
        percent = 1
    
    if percent_of != None:
        return int(percent * percent_of)
    
    return percent;

@register.simple_tag
def account_user_count(session):
    return SESSION.get_patronStore_count(session)
    
@register.simple_tag
def account_message_count(session):
   return SESSION.get_message_count(session)
