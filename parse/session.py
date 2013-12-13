"""
Use to keep track of all the cache object names in the session.

Note that all get lists return a maximum of 900.
"""
import pytz

from django.utils import timezone
from libs.dateutil.relativedelta import relativedelta

from parse.apps.employees import PENDING, APPROVED
from parse.apps.messages import FEEDBACK, BASIC, OFFER

# Note another thing in the session is the 
# django.contrib.auth.SESSION_KEY ehose value is the Parse
# session token received on login

# If not PRODUCTION_SERVER, the DEVELOPMENT_TOKEN may also be here
SESSION_CACHE = [
    # temps
    'message_count',
    'patronStore_count', # PUSH
    'store_timezone',
    "active_store_location_id",
    
    # actual objects
    'account',
    'store', # PUSH 
    'store_locations',
    'subscription',
    'settings',
    'employees_pending_list', # PUSH
    'employees_approved_list',
    'messages_sent_list',
    'messages_received_list', # PUSH
    'redemptions_pending', # PUSH
    'redemptions_past', # PUSH
    
    'employee', # if employee is logged in
    
]

def get_store(session):
    # WARNING! If employee is logged in, therefore the employee is not
    # the store owner and the account may have a null Store or 
    # a Store different from what is expected!
    if "store" not in session:
        if 'employee' in session:
            store = session['employee'].get("store")
        else:
            store = session['account'].get('store')
            
        session['store'] = store
        
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

    return session['redemptions_past']
        
def get_store_locations(session):
    """ limit of 500 store locations for now """
    if "store_locations" not in session:
        store = get_store(session)
        store_locations = {}
        for sl in store.get("storeLocations", order="createdAt", limit=500):
            store_locations[sl.objectId] = sl
        session['store_locations'] = store_locations
        
    return session['store_locations']
        
def get_active_store_location_id(session):
    if 'active_store_location_id' not in session:
        # pick a random store location
        session['active_store_location_id'] =\
            get_store_locations(session).keys()[0]
        
    return session['active_store_location_id']
    
def get_store_location(session, store_location_id):
    return get_store_locations(session).get(store_location_id)
        
def get_store_timezone(session):
    """ returns the pytz.timezone object """
    if "store_timezone" not in session:
        store_location = get_store_location(session,
            get_active_store_location_id(session))
        session['store_timezone'] =\
            pytz.timezone(store_location.get('store_timezone'))

    return session['store_timezone']
        
def get_patronStore_count(session):
    if 'patronStore_count' not in session:
        patronStore_count =\
            get_store(session).get("patronStores", count=1, limit=0)
        session['patronStore_count'] = patronStore_count
        
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
        
    return session['employees_approved_list']
     
def get_subscription(session):
    if "subscription" not in session:
        session['subscription'] = get_store(session).get("subscription")
        
    return session['subscription']

def get_settings(session):
    if "settings" not in session:
        session['settings'] = get_store(session).get("settings")
        
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
        
    return session['message_count']
    
def load_all(session, commit=True):
    """
    Loads calls all loadeers for each in SESSION_CACHE
    """
    get_store(session)
    get_redemptions_pending(session)
    get_redemptions_past(session)
    get_store_timezone(session)
    get_patronStore_count(session)
    get_messages_sent_list(session)
    get_messages_received_list(session)
    get_employees_pending_list(session)
    get_employees_approved_list(session)
    get_subscription(session)
    get_settings(session)
    get_message_count(session)
    
    if commit:
        session.save()
    
    
