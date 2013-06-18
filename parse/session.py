"""
Use to keep track of all the cache object names in the session.
"""

from datetime import date

from libs.dateutil.extras import start_month, end_month

from parse.apps.employees import PENDING, APPROVED
from parse.apps.messages import FEEDBACK

SESSION_CACHE = [
    'message_count',
    'feedback_unread', # need push notification
    'employees_pending', # need push notification
    'patronStore_count', # need push notification
    
    # actual objects
    'account',
    'store', # need push notification (for rewards)
    'subscription',
    'settings',
    'employees_pending_list', # need push notification
    'employees_approved_list',
    'messages_sent_list',
    'messages_received_list', # need push notification
]

def get_store(session):
    if "store" not in session:
        store = session['account'].get('store')
        session['store'] = store
        return store
    else:
        return session['store']
        
def get_patronStore_count(session):
    if 'patronStore_count' not in session:
        patronStore_count =\
            get_store(session).get("patronStores", count=1, limit=0)
        session['patronStore_count'] = patronStore_count
        return patronStore_count
    else:
        return session['patronStore_count']
        
def get_messages_sent_list(session):
    if 'messages_sent_list' not in session:
        store = get_store(session)
        messages_sent_list = store.get("sentMessages")
        # make sure that the list is a list and not none
        if messages_sent_list is None:
            messages_sent_list = []
        session['messages_sent_list'] = messages_sent_list
        
        # make sure that the store's cache is None, otherwise bad!
        store.sentMessages = None
        session['store'] = store
        
        return messages_sent_list
    else:
        return session['messages_sent_list']
        
def get_messages_received_list(session):
    # when a store replies, it also gets stored in the received
    # with message type BASIC or OFFER
    if 'messages_received_list' not in session:
        store = get_store(session)
        messages_received_list = store.get(\
                    "receivedMessages", message_type=FEEDBACK)
        
        # make sure that the list is a list and not none
        if messages_received_list is None:
            messages_received_list = []
        session['messages_received_list'] = messages_received_list
        
        # make sure that the store's cache is None, otherwise bad!
        store.receivedMessages = None
        session['store'] = store
        
        return messages_received_list
    else:
        return session['messages_received_list']
        
def get_message_count(session):
    if 'message_count' not in session:
        today = date.today()
        message_count = get_store(session).get(\
            'sentMessages', 
            createdAt__gte=start_month(today),
            createdAt__lte=end_month(today),
            count=1, limit=0)
        session['message_count'] = message_count
    else:
        message_count = session['message_count']
    return message_count
        
def get_feedback_unread(session):
    if 'feedback_unread' not in session:
        feedback_unread = get_store(session).get(\
            "receivedMessages", is_read=False, 
            message_type=FEEDBACK, count=1, limit=0)
        session['feedback_unread'] = feedback_unread
    else:
        feedback_unread = session['feedback_unread']
    return feedback_unread
    
def get_employees_pending(session):
    if 'employees_pending' not in session:
        employees_pending = get_store(session).get(\
                'employees', status=PENDING, count=1, limit=0)
        session['employees_pending'] = employees_pending
    else:
        employees_pending = session['employees_pending']
    return employees_pending
       
def get_employees_pending_list(session):
    if 'employees_pending_list' not in session:
        store = get_store(session)
        employees_pending_list = get_store(session).get(\
                                "employees", status=PENDING)
                                
        # make sure that the list is a list and not none
        if employees_pending_list is None:
            employees_pending_list = []
        session['employees_pending_list'] = employees_pending_list
        
        # make sure that the store's cache is None, otherwise
        # getting pending_list might return the approved_list!
        store.employees = None
        session['store'] = store
        
        return employees_pending_list
    else:
        return session['employees_pending_list']
        
def get_employees_approved_list(session):
    if 'employees_approved_list' not in session:
        store = get_store(session)
        employees_approved_list = store.get(\
                                "employees", status=APPROVED)      
        
        # make sure that the list is a list and not none
        if employees_approved_list is None:
            employees_approved_list = []  
        session['employees_approved_list'] = employees_approved_list
            
        # make sure that the store's cache is None, otherwise
        # getting pending_list might return the approved_list!
        store.employees = None
        session['store'] = store
        
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
