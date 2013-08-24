from __future__ import division
from django import template
from dateutil import parser
from datetime import datetime

from parse.utils import parse
from parse.apps.accounts import sub_type
from parse import session as SESSION

register = template.Library()

@register.simple_tag
def account_user_usage(session, percent_of=None):
    atype = sub_type[SESSION.get_subscription(\
                session).get('subscriptionType')]
        
    num_patrons = SESSION.get_patronStore_count(session)
    
    if atype['max_users'] == -1:
        percent = 0
    else:
        # may cause division by 0!!!
        percent = num_patrons / atype['max_users']
        if(percent > 1):
            percent = 1
    
    if percent_of != None:
        return int(percent * percent_of)
            
    return percent;

@register.assignment_tag
def account_alert(session):
    atype = sub_type[SESSION.get_subscription(\
                session).get('subscriptionType')]
    
    num_patrons = SESSION.get_patronStore_count(session)
        
    # may cause division by 0!!!
    percent = float(num_patrons) / float(atype['max_users'])
    
    #if they are at 80 percent of their users, alert
    if percent >= .8:
        return 1
    elif percent >= 1.0:
        return 2
    return 0
    

@register.assignment_tag
def account_is_admin(session):
    return SESSION.get_store(session).is_admin(session['account'])
        
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
