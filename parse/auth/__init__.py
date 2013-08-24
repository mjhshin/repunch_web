"""
Authentication backend for Parse
"""

import hashlib, uuid, pytz
from django.contrib.auth import SESSION_KEY

from repunch.settings import PAGINATION_THRESHOLD
from parse.utils import parse
from parse.apps.accounts.models import Account
from libs.repunch import rputils

def hash_password(password):
    """ returns the hash of the raw password """
    # NOT USED ATM
    return hashlib.sha1(password).hexdigest()

def login(request, requestDict):
    """ 
    This combines Django's authenticate and login functions.
    The request.POST must contain a username and password.

    If authentication is successful, account is updated_locally
    and adds the appropriate data to the request so that the user/
    account is recognized to be logged in.
    
    This will also cache some of the store's info in the session.
    Also checks if the store is active or not.
    
    Returns an Account object if the account subscription is active 
    and username and passwords are good. Otherwise, 0 if bad login 
    credentials (wrong pass or pointer to store does not exist) 
    and 1 if subscription is not active,
    2 if employee but no access.
    """
    # first check if the request is already logged in 
    if request.session.get('account'):
        return request.session.get('account')
    
    # note that email is the same as username
    res = parse("GET", "login", query=\
                {"username":requestDict.get('username'),
                 "password":requestDict.get('password')} )
                    
    if res and "error" not in res:
        account = Account(**res)
        account.fetch_all()
        store = account.store
        # if the User object has a store then we are good to go
        if store: 
            # check if employee with no access level
            if not store.has_access(account):
                return 2
            
            store = account.get('store')
            settings = store.get("settings")
            subscription = store.get("subscription")
        
            if store.get('active'):
                # flush the session first to assign a new session_key
                request.session.flush()
            
                request.session[SESSION_KEY] = res.get('sessionToken')
                
                # store in session cache
                request.session['subscription'] = subscription
                request.session['settings'] = settings
                request.session['store'] = store
                request.session['account'] = account
                
                if store.get('store_timezone'):
                    rputils.set_timezone(request, 
                        pytz.timezone(store.get('store_timezone')))
                        
                # for stores that have not yet uploaded a store avatar
                # need to set this back to True on upload success
                request.session['has_store_avatar'] =\
                    store.get("store_avatar") is not None
                        
                # If value is None, the session reverts to using 
                # the global session expiry policy.
                if "stay_in" in requestDict:
                    request.session.set_expiry(None)
                # If value is 0, the user's session cookie will 
                # expire when the user's Web browser is closed.
                else:
                    request.session.set_expiry(0)
                
                return account
            else:
                return 1
        else:
            return 0
    else:
        return 0
