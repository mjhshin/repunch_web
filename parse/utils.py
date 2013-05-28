"""
Helpers methods for parse.apps to enfore the DRY principle.
"""

import json, httplib, urllib
from django.contrib.auth.hashers import make_password

from repunch.settings import PARSE_VERSION, REST_CONNECTION_META
from parse.apps.accounts.models import Account    

def parse(method, path, data=None, query=None):
    """
    sends a request to parse using specified method, url, data,
    and optionally a query.
    
    data is a dictionary/json, usually it is a ParseObject.__dict__
    query is a dictionary/json containing constraints for filtering.
    However, query must be a string (objectId) if method is PUT
    Note that is the method is GET, data parameter is ignored.

    Returns None if request does not return a json object.
    """
    conn = httplib.HTTPSConnection('api.parse.com', 443)
    conn.connect()

    if method == "POST":
        conn.request("POST", '/' + PARSE_VERSION + '/' + path, 
                        json.dumps(data), REST_CONNECTION_META)
    elif method == "GET":
        if query:
            params = '?' + urllib.urlencode({"where":\
                                        json.dumps(query)})
        else:
            params = ''
        conn.request("GET", '/' + PARSE_VERSION + '/' + path +\
                '%s' % (params, ), '',  REST_CONNECTION_META)

    elif method == "PUT":
        conn.request("PUT", '/' + PARSE_VERSION + '/' + path+\
                '%s' % (query, ), '', json.dumps(data),
                REST_CONNECTION_META)

    try:
        result = json.loads(conn.getresponse().read())
    except ValueError:
        result = None

    conn.close()
    return result


def authenticate(user, raw_pass):
    """ returns True if the hash of raw_pass == the pass in the DB.
        pass2 is the hash stored in the DB- which is hashed. 
        Returns the Account object if successful, otherwise None.
    """
    res = parse("GET", user.path(), query)
    















