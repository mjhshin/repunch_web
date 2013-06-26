"""
Use to keep track of all the cache object names in the session.
"""
import pytz

from django.utils import timezone
from libs.dateutil.relativedelta import relativedelta
from libs.dateutil.extras import start_month, end_month

from parse.apps.employees import PENDING, APPROVED
from parse.apps.messages import FEEDBACK

SESSION_CACHE = [
    'message_count',
    'feedback_unread', # need push notification
    'employees_pending', # need push notification
    'patronStore_count', # need push notification
    
    'store_timezone', # DO NOT USE DATETIME! ALWAYS USE TIMEZONE!
    
    # actual objects
    'account',
    'store', # need push notification (for rewards)
    'subscription',
    'settings',
    'employees_pending_list', # sync with employees_pending
    'employees_approved_list',
    'messages_sent_list',
    'messages_received_list', # sync with feedback_unread
    
    'redemptions',
    'remptions_past',
    
    # time in which all comet processes for the request will die
    # 'stop_comet_time', unused at the moment
]

def get_store(session):
    if "store" not in session:
        store = session['account'].get('store')
        session['store'] = store
        return store
    else:
        return session['store']
        
def get_redemptions(session):
    """ 
    returns all the unredeemed redemptions.
    """
    if "redemptions" not in session:
        store = get_store(session)
        redemptions = store.get('redeemRewards', is_redeemed=False,
                        order="-createdAt")
        if redemptions is None:
            redemptions = []
            
        store.redeemRewards = None
        session['store'] = store
        session['redemptions'] = redemptions
        return redemptions
    else:
        return session['redemptions']
        
def get_redemptions_past(session):
    """ 
    returns all the redeemed redemptions.
    """
    if "redemptions_past" not in session:
        store = get_store(session)
        redemptions = store.get('redeemRewards', is_redeemed=True,
                        order="-createdAt")
        if redemptions is None:
            redemptions = []
            
        store.redeemRewards = None
        session['store'] = store
        session['redemptions_past'] = redemptions
        return redemptions
    else:
        return session['redemptions_past']
        
def get_store_timezone(session):
    """ returns the pytz.timezone object """
    if "store_timezone" not in session:
        store_timezone =\
            pytz.timezone(get_store(session).get('store_timezone'))
        session['store_timezone'] = store_timezone
        return store_timezone
    else:
        return session['store_timezone']
        
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
        messages_sent_list = store.get("sentMessages",
                                order="-createdAt")
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
                    "receivedMessages", message_type=FEEDBACK,
                    order="-createdAt")
        
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
        
def get_message_count(session, time_now):
    if 'message_count' not in session:
        now = time_now
        message_count = get_store(session).get(\
            'sentMessages', 
            createdAt__gte=start_month(now),
            createdAt__lte=end_month(now),
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
                                "employees", status=PENDING,
                                order="-createdAt")
                                
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
                                "employees", status=APPROVED,
                                order="-createdAt")     
        
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
