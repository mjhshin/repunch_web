"""
Authentication backend for Parse
"""

import hashlib, uuid, pytz
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.backends.cache import SessionStore

from libs import recaptcha
from libs.repunch import rputils
from libs.repunch.rputils import delete_after_delay
from apps.comet.models import CometSession, CometSessionIndex
from repunch.settings import PAGINATION_THRESHOLD, COMET_PULL_RATE,\
PRODUCTION_SERVER, RECAPTCHA_TOKEN, RECAPTCHA_ATTEMPTS
from parse import session as SESSION
from parse.utils import account_login, flush
from parse.apps.accounts.models import Account
from parse.apps.employees import PENDING


def logout(request, reverse_url):
    session_key = request.session.session_key
    flush(request.session)
    
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

def login(request, requestDict, no_recaptcha=False):
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
    2 if employee but no access, 3 if employee is still pending,
    4 if RECAPTCHA_TOKEN in session and recaptcha response fails.
    """
    # first check if the request is already logged in 
    if request.session.get('account'):
        return request.session.get('account')
        
    # now check for recaptcha
    if not no_recaptcha and RECAPTCHA_TOKEN in request.session and\
        request.session[RECAPTCHA_TOKEN] >= RECAPTCHA_ATTEMPTS:
        is_valid = recaptcha.submit(request,
            requestDict['recaptcha_challenge_field'],
            requestDict['recaptcha_response_field']).is_valid
        if not is_valid:
            return 4
    
    # note that email is the same as username
    # email needs to be stripped and lowered
    res = account_login(requestDict['username'].strip().lower(),
        requestDict['password'])
                    
    if res and "error" not in res:
        # correct login credentials - remove recaptcha token if exist
        if not no_recaptcha:
            recaptcha.login_success(request.session,
                requestDict['username'])
    
        account = Account(**res)
        account.fetch_all()
        
        # If the Account has both a Store and Employee object,
        # log the user in as the Store owner - not employee
        store = None
        if account.Store:
            store = account.store
            account_type = "store"
        elif account.Employee:
            store = account.employee.get("store")
            employee = account.employee
            account_type = "employee"
        
        # if the User object has a store then we are good to go
        if store: 
            store.fetch_all()
        
            # check if employee with no access level or still pending
            if account_type == "employee":
                if employee.status == PENDING:
                    return 3
                elif not store.has_access(account):
                    return 2
            
            settings = store.get("settings")
            subscription = store.get("subscription")
        
            if store.get('active'):
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
                
                if account_type == "employee":
                    request.session['employee'] = employee
                
                SESSION.load_all(request.session)
                        
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
            if not no_recaptcha:
                recaptcha.login_fail(request.session,
                    requestDict['username'])
            return 0
    else:
        if not no_recaptcha:
            recaptcha.login_fail(request.session,
                requestDict['username'])
        return 0
