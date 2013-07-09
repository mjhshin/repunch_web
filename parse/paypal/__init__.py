"""
This will replace the paypalrestsdk.
https://github.com/paypal/rest-api-sdk-python

Reason being unreliable.
"""

import pycurl, json, urllib2
from StringIO import StringIO
from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from repunch.settings import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET,\
PAYPAL_ENDPOINT
from libs.repunch.rpccutils import get_cc_type

# to be safe, use the getter methods instead of importing these
ACCESS_TOKEN = None
# datetime objects in UTC
ACCESS_TOKEN_EXPIRES_IN = None

def get_access_token():
    """ 
    First checks if the access tokens exists or has not expired.
    Will automatically refresh the ACCESS_TOKEN.
    
    returns the ACCESS_TOKEN 
    """
    if not ACCESS_TOKEN or timezone.now() > ACCESS_TOKEN_EXPIRES_IN:
        _refresh_access_token()
    return ACCESS_TOKEN

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
    
    global ACCESS_TOKEN, ACCESS_TOKEN_EXPIRES_IN
    # update 
    ACCESS_TOKEN = res['access_token']
    # subtract 5 mins (300 seconds) to be safe
    ACCESS_TOKEN_EXPIRES_IN = timezone.now() +\
                    relativedelta(seconds=res['expires_in']-300)

def store_cc(subscription, cc_number, cvv2):
    """
    Stores a paypal credit card id to the subscription's ppid.
    This uses urllib2 instead of pycurl because pycurl does not work 
    here for some reason.
    
    returns the result of the api call.
    """
    url = 'https://' + PAYPAL_ENDPOINT + '/v1/vault/credit-card'
    data = json.dumps({
        "payer_id": "%s" % str(subscription.objectId),
        "type": "%s" % str(get_cc_type(cc_number)),
        "number": "%s" % str(cc_number),
        "cvv2": "%s" % str(cvv2),
        "expire_month":\
            "%s" % str(subscription.date_cc_expiration.month),
        "expire_year":\
            "%s" % str(subscription.date_cc_expiration.year),
        "first_name": "%s" % str(subscription.first_name),
        "last_name": "%s" % str(subscription.last_name),
    })
    
    req = urllib2.Request(url,
        headers = {
            "Content-Type": "application/json",
            "Authorization": 'Bearer ' + str(get_access_token())
        }, data=data)

    return json.loads(urllib2.urlopen(req).read())
    
def charge_cc(subscription, total, description):
    """
    Uses that stored credit card via the subscription's pp_cc_id.
    Returns the result of the payment.
    """
    url = 'https://' + PAYPAL_ENDPOINT + '/v1/payments/payment'
    data = json.dumps({
        "intent": "sale",
        "payer": {
            "payment_method": "credit_card",
            "funding_instruments": [
                {
                    "credit_card_token": {
                        "credit_card_id": subscription.pp_cc_id,
                        "payer_id": subscription.objectId,
                    }
                }
            ]
        },
        "transactions": [
            {
                "amount": {
                    "total": "%.2f" % float(total),
                    "currency": "USD"
                },
                "description": description
            }
        ]
    })
    
    req = urllib2.Request(url,
        headers = {
            "Content-Type": "application/json",
            "Authorization": 'Bearer ' + str(get_access_token())
        }, data=data)

    return json.loads(urllib2.urlopen(req).read())
    
def delete_cc(subscription):
    """
    Delete the stored credit card in paypal.
    This should be called upon creation of a new credit card for the 
    same user.
    """
    pass
