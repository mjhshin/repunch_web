"""
Use to keep track of all the cache object names in the session.
"""

from parse.apps.employees import PENDING, APPROVED
from parse.apps.messages import FEEDBACK

SESSION_CACHE = [
    'num_patrons',
    'message_count',
    'user_count',
    'unread_feedback',
    'employees_pending',
    'patronStore_count',
    
    # actual objects
    'account',
    'store',
    'subscription',
    'settings',
    'employees_pending_list',
    'employees_approved_list',
    'messages_sent_list',
    'messages_received_list',
]

def get_store(session):
    if "store" not in session:
        store = session['account'].get('store')
        session['store'] = store
        return store
    else:
        return session['store']
        
def get_messages_sent_list(session):
    if 'messages_sent_list' not in session:
        messages_sent_list = get_store(session).get(\
                                    "sentMessages")
        session['messages_sent_list'] = messages_sent_list
        return messages_sent_list
    else:
        return session['messages_sent_list']
        
def get_patronStore_count(session):
    if 'patronStore_count' not in session:
        patronStore_count =\
            get_store(session).get("patronStores", count=1, limit=0)
        session['patronStore_count'] = patronStore_count
        return patronStore_count
    else:
        return session['patronStore_count']
        
def get_messages_received_list(session):
    # when a store replies, it also gets stored in the received
    # with message type BASIC or OFFER
    if 'messages_received_list' not in session:
        messages_received_list = get_store(session).get(\
                    "receivedMessages", message_type=FEEDBACK)
        session['messages_received_list'] = messages_received_list
        return messages_received_list
    else:
        return session['messages_received_list']
        
def get_employees_pending_list(session):
    if 'employees_pending_list' not in session:
        employees_pending_list = get_store(session).get(\
                                "employees", status=PENDING)
        session['employees_pending_list'] = employees_pending_list
        return employees_pending_list
    else:
        return session['employees_pending_list']
        
def get_employees_approved_list(session):
    if 'employees_approved_list' not in session:
        employees_approved_list = get_store(session).get(\
                                "employees", status=APPROVED)
        session['employees_approved_list'] = employees_approved_list
        return employees_approved_list
    else:
        return session['employees_approved_list']
     
def get_subscription(session):
    if "subscription" not in session:
        subscription = get_store(session).get("subscription")
        session['subscription'] = subscription
        return subscription
    else:
        return session['subscription']

def get_settings(session):
    if "settings" not in session:
        settings = get_store(session).get("settings")
        session['settings'] = settings
        return settings
    else:
        return session['settings']
