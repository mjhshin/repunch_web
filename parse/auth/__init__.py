"""
Authentication backend for Parse
"""

import hashlib, uuid
from django.contrib.auth import SESSION_KEY

from repunch.settings import PAGINATION_THRESHOLD
from parse.utils import parse

def hash_password(password):
    """ returns the hash of the raw password """
    # NOT USED ATM
    return hashlib.sha1(password).hexdigest()

def login(request, username, password, account):
    """ 
    This combines Django's authenticate and login functions.
    account is a new Account to prevent having to import Account.

    If authentication is successful, account is updated_locally
    and adds the appropriate data to the request so that the user/
    account is recognized to be logged in.
    
    This will also cache some of the store's info in the session.
    """
    #res = parse("GET", "login", query={"username":username,
    #                "password":hash_password(password)} )
    
    res = parse("GET", "login", query={"username":username,
                    "password":password} )
    # TODO maybe share the session with same user on different browser
    if res and "error" not in res:
        request.session[SESSION_KEY] = res.get('sessionToken')
        account.update_locally(res, False)
        # retrieve all store info for caching except some data
        store = account.get('store')
        # Pointers
        settings = store.get("settings")
        settings.fetchAll()
        subscription = store.get("subscription")
        subscription.fetchAll()
        
        # this does not work. See see cache notes.
        # store.set("settings", settings)
        # store.set("subscription", subscription)
        request.session['subscription'] = subscription
        request.session['settings'] = settings
        request.session['store'] = store
        request.session['account'] = account
        return account
    else:
        return None
