"""
Authentication backend for Parse
"""

import hashlib, uuid
from django.contrib.auth import SESSION_KEY

from parse.utils import parse

def hash_password(password):
    """ returns the hash of the raw password """
    return hashlib.sha1(password).hexdigest()

def login(request, username, password, account):
    """ 
    This combines Django's authenticate and login functions.
    account is a new Account to prevent having to import Account.

    returns True if the hash of raw_pass == the pass in the DB.
    pass2 is the hash stored in the DB- which is hashed. 
    Returns the Account object if successful, otherwise None.

    If authentication is successful, account is updated_locally
    and adds the appropriate data to the request so that the user/
    account is recognized to be logged in.
    """
    res = parse("GET", "login", query={"username":username,
                    "password":hash_password(password)} )
    if res and "error" not in res:
        account.update_locally(res)
        request.session[SESSION_KEY] = account.sessionToken
        request.session['account'] = account
        return account
    else:
        return None
