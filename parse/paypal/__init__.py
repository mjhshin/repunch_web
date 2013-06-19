"""
This will replace the paypalrestsdk.
https://github.com/paypal/rest-api-sdk-python

Reason being unreliable.
"""

import pycurl, json
from StringIO import StringIO

from libs.dateutil.relativedelta import relativedelta
from repunch.settings import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET,\
PAYPAL_ENDPOINT

# to be safe, use the getter methods instead of importing these
ACCESS_TOKEN = None
# datetime objects
ACCESS_TOKEN_EXPIRES_IN = None
LAST_ACCESS_TIME = None

def get_access_token():
    """ 
    First checks if the access tokens exists or has not expired.
    Will automatically refresh the ACCESS_TOKEN.
    
    returns the ACCESS_TOKEN 
    """
    if not ACCESS_TOKEN or 
    
    return ACCESS_TOKEN

# TODO set up celery to call this method every x seconds
def _refresh_access_token():
    """
    Must be called after every x seconds. x is acquired from the 
    reponse's expires_in field.
    
    returns a dictionary containing the results.
    """
    url = 'https://' + PAYPAL_ENDPOINT + '/v1/oauth2/token'
    res = StringIO()

    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
    c.setopt(pycurl.HTTPHEADER, ['Accept-Language: en_US'])
    c.setopt(pycurl.USERPWD, PAYPAL_CLIENT_ID + ':' +\
                PAYPAL_CLIENT_SECRET)
    c.setopt(c.WRITEFUNCTION, res.write)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, 'grant_type=client_credentials')
    # perform automatically returns a value and exits this method
    c.perform()
    res = json.loads(res.getvalue())
    
    # update 
    ACCESS_TOKEN = res['access_token']
    # need to convert to datetime object from seconds 28800 to
    # 
    ACCESS_TOKEN_EXPIRES_IN = res['expires_in']
    LAST_ACCESS_TIME = datetime.now()

def store_cc(subscription, cc_number, ):
    """
    Stores a paypal credit card id to the subscription's ppid.
    """
    pass
