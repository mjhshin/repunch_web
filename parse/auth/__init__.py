"""
Authentication backend for Parse
"""

import hashlib, uuid, pytz
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.backends.cache import SessionStore

from libs.repunch import rputils
from libs.repunch.rputils import delete_after_delay
from apps.comet.models import CometSession, CometSessionIndex
from repunch.settings import PAGINATION_THRESHOLD, COMET_PULL_RATE,\
PRODUCTION_SERVER
from parse import session as SESSION
from parse.utils import parse
from parse.apps.accounts.models import Account
from parse.apps.employees import PENDING

def hash_password(password):
    """ returns the hash of the raw password """
    # NOT USED ATM
    return hashlib.sha1(password).hexdigest()
    

def logout(request, reverse_url):
    session_key = request.session.session_key
    # flush immediately
    request.session.flush()
    print "Logged out"
    print "SESSION KEY: " + session_key
    print SessionStore(session_key)._get_session()
    print "NEW SESSION KEY: " + request.session.session_key
    
    # first delete the CometSessionIndex
    try:
        csi = CometSessionIndex.objects.get(session_key=session_key)
        csi.delete()
    except CometSessionIndex.DoesNotExist:
        pass
    
    # set all related cometsessions to modified to flag all existing
    # tabs of the logout and delete them after a delay
    cs = CometSession.objects.filter(session_key=session_key)
    for c in cs:
        c.modified = True
        c.save()
    delete_after_delay(cs, COMET_PULL_RATE + 3)
    return redirect(reverse(reverse_url))

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
    2 if employee but no access, 3 if employee is still pending.
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
        
        # TODO in the future when an account may have a Store and
        # Employee, we need to differentiate which 1 the user
        # wants to login as. 
        if account.Employee:
            store = account.employee.get("store")
            employee = account.employee
            account_type = "employee"
        elif account.Store:
            store = account.store
            account_type = "store"
        
        # if the User object has a store then we are good to go
        if store: 
            if account_type == "employee" and\
                employee.status == PENDING:
                return 3
            # check if employee with no access level or still pending
            elif not store.has_access(account):
                return 2
            
            settings = store.get("settings")
            subscription = store.get("subscription")
        
            if store.get('active'):
                # clear the session but do not assign a new sessionkey
                request.session.clear()
                request.session.delete()
            
                request.session[SESSION_KEY] = res.get('sessionToken')
                
                # load all cache data!
                # IMPORTANT for parse.comet.receive to work properly
                # reason is that if user stays in 1 page, not all
                # cache data is loaded and things go wrong-
                # e.g. sending message from window 1 does not update
                # the message count in window 2
                request.session['subscription'] = subscription
                request.session['settings'] = settings
                request.session['store'] = store
                request.session['account'] = account
                SESSION.load_all(request.session)
                
                # moved to SESSION.load_all
                #if store.get('store_timezone'):
                #    # the store timezone is inserted into the request
                #    rputils.set_timezone(request, 
                #        pytz.timezone(store.get('store_timezone')))
                        
                # for stores that have not yet uploaded a store avatar
                # need to set this back to True on upload success
                #request.session['has_store_avatar'] =\
                #    store.get("store_avatar") is not None
                        
                # If value is None, the session reverts to using 
                # the global session expiry policy.
                if "stay_in" in requestDict and PRODUCTION_SERVER:
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
