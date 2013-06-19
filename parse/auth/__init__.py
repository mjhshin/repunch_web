"""
Authentication backend for Parse
"""

import hashlib, uuid
import pytz
from django.contrib.auth import SESSION_KEY

from repunch.settings import PAGINATION_THRESHOLD
from parse.utils import parse
from parse.apps.accounts.models import Account
from libs.repunch import rputils

def hash_password(password):
    """ returns the hash of the raw password """
    # NOT USED ATM
    return hashlib.sha1(password).hexdigest()

def login(request):
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
    credentials and 1 if subscription is not active.
    """
    res = parse("GET", "login", query=\
                {"username":request.POST['username'],
                 "password":request.POST['password']} )
                    
    # TODO maybe share the session with same user on different browser
    if res and "error" not in res:
        account = Account(**res)
        store = account.get('store')
        settings = store.get("settings")
        subscription = store.get("subscription")
    
        if subscription.get('active'):
            request.session[SESSION_KEY] = res.get('sessionToken')
            settings.fetchAll()
            subscription = store.get("subscription")
            subscription.fetchAll()
            
            # store in session cache
            request.session['subscription'] = subscription
            request.session['settings'] = settings
            request.session['store'] = store
            request.session['account'] = account
            
            rputils.set_timezone(request, 
                pytz.timezone(store.get('store_timezone')))
            
            return account
        else:
            return 1
    else:
        return 0
