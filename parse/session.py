"""
Use to keep track of all the cache object names in the session.

Note that all get lists return a maximum of 900.
"""
import pytz

from django.utils import timezone
from libs.dateutil.relativedelta import relativedelta

from parse.apps.employees import PENDING, APPROVED
from parse.apps.messages import FEEDBACK, BASIC, OFFER

SESSION_CACHE = [
    # temps
    'message_count',
    'patronStore_count', # PUSH
    'store_timezone',
    "has_store_avatar", 
    
    # actual objects
    'account',
    'store', # PUSH (for rewards)
    'subscription',
    'settings',
    'employees_pending_list', # PUSH
    'employees_approved_list',
    'messages_sent_list',
    'messages_received_list', # PUSH
    'redemptions_pending', # PUSH
    'redemptions_past', # PUSH
    
    'comet_time', # used by the comet mechanism
]

def get_store(session):
    if "store" not in session:
        store = session['account'].get('store')
        session['store'] = store
        return store
    else:
        return session['store']
        
def get_redemptions_pending(session):
    """ 
    returns all the pending redemptions (limit of 900)
    """
    if "redemptions_pending" not in session:
        store = get_store(session)
        redemptions_pending = store.get('redeemRewards',
                    is_redeemed=False, order="-createdAt", limit=900)
        if redemptions_pending is None:
            redemptions_pending = []
            
        store.redeemRewards = None
        session['store'] = store
        session['redemptions_pending'] = redemptions_pending
        return redemptions_pending
    else:
        return session['redemptions_pending']
        
def get_redemptions_past(session):
    """ 
    returns all the redeemed redemptions (limit of 900)
    Ordered based on updatedAt attr.
    """
    if "redemptions_past" not in session:
        store = get_store(session)
        redemptions = store.get('redeemRewards', is_redeemed=True,
                        order="-createdAt", limit=900)
        if redemptions is None:
            redemptions = []
        #else:
        #    redemptions.sort(key=lambda k: k.updatedAt, reverse=True)
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
    """ 
    This is what will be displayed in the Message tab in the dashboard
    so this does not include replies to feedbacks, which have the
    message_type of FEEDBACK.
    """
    if 'messages_sent_list' not in session:
        store = get_store(session)
        messages_sent_list = store.get("sentMessages",
                            message_type1=BASIC, message_type2=OFFER,
                            order="-createdAt", limit=900)
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
    if 'messages_received_list' not in session:
        store = get_store(session)
        messages_received_list = store.get(\
                    "receivedMessages", message_type=FEEDBACK,
                    order="-createdAt", limit=900)
        
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
       
def get_employees_pending_list(session):
    if 'employees_pending_list' not in session:
        store = get_store(session)
        employees_pending_list = get_store(session).get(\
                                "employees", status=PENDING,
                                order="-createdAt", limit=900)
                                
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
                                order="-createdAt", limit=900)     
        
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
        
def get_message_count(session):
    """ 
    Returns the number of messages sent from their last_date_billed
    to now.
    """
    if 'message_count' not in session:
        date_last_billed =\
            get_subscription(session).get("date_last_billed")
        message_count = get_store(session).get(\
            'sentMessages', 
            createdAt__gte=date_last_billed,
            message_type1=BASIC,
            message_type2=OFFER,
            count=1, limit=0)
        session['message_count'] = message_count
    else:
        message_count = session['message_count']
    return message_count
