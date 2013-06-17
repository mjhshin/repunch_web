from __future__ import division
from django import template
from datetime import date
from dateutil import parser

from libs.dateutil.extras import start_month, end_month
from parse.utils import parse
from parse.apps.accounts import sub_type
from parse import session as SESSION

register = template.Library()

@register.simple_tag
def account_user_usage(session, percent_of=None):
    atype = sub_type[SESSION.get_subscription(\
                session).get('subscriptionType')]
        
    if 'num_patrons' not in session:
        num_patrons = SESSION.get_store(session).get('patronStores', 
                        count=1, limit=0)
        session['num_patrons'] = num_patrons
    else:
        num_patrons = session['num_patrons']
    
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
    
    if 'num_patrons' not in session:
        num_patrons = SESSION.get_store(session).get(\
                        'patronStores', count=1, limit=0)
        session['num_patrons'] = num_patrons
    else:
        num_patrons = session['num_patrons']
        
    # may cause division by 0!!!
    percent = num_patrons / atype['max_users']
    
    #if they are at 80 percent of their users, alert
    return (percent >= .8)

@register.simple_tag
def account_message_usage(session, percent_of=None):
    atype = sub_type[SESSION.get_subscription(\
                session).get('subscriptionType')]
    
    if 'message_count' not in session:
        today = date.today()
        message_count = SESSION.get_store(session).get(\
            'sentMessages', 
            createdAt__gte=start_month(today),
            createdAt__lte=end_month(today),
            count=1, limit=0)
        session['message_count'] = message_count
    else:
        message_count = session['message_count']
    
    
    percent = message_count/atype['max_messages']
    if(percent > 1): #don't go past 1
        percent = 1
    
    if percent_of != None:
        return int(percent * percent_of)
    
    return percent;

@register.simple_tag
def account_user_count(session):
    if 'user_count' not in session:
        user_count = SESSION.get_store(session).get('patronStores', 
            count=1, limit=0)
    else:
        user_count = session['user_count']
    return user_count
    

@register.simple_tag
def account_message_count(session):
    if 'message_count' not in session:
        today = date.today()
        message_count = SESSION.get_store(session).get('sentMessages', 
            createdAt__gte=start_month(today),
            createdAt__lte=end_month(today),
            count=1, limit=0)
        session['message_count'] = message_count
    else:
        message_count = session['message_count']
    return message_count
