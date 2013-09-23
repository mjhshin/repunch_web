"""
Taken from http://recaptcha.googlecode.com/svn/trunk/recaptcha-plugins/python/recaptcha/client/captcha.py

Pip wasn't installing it properly so just copy and pasted this source here.
The original code has been modified.
"""

import urllib2, urllib

from apps.accounts.models import RecaptchaToken
from repunch.settings import RECAPTCHA_PUBLIC_KEY,\
RECAPTCHA_PRIVATE_KEY, RECAPTCHA_ATTEMPTS, RECAPTCHA_TOKEN,\
PRODUCTION_SERVER

API_SSL_SERVER="https://www.google.com/recaptcha/api"
API_SERVER="http://www.google.com/recaptcha/api"
VERIFY_SERVER="www.google.com"

def get_client_ip(request):
    """ This is not part of the original code """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
    
def login_fail(session, username):
    """ 
    Call this if the user tried to login with the given username
    and failed. 
    
    This will create a Recaptcha token if 1 does not yet exist for the
    username or increment the attempts. Note that this will not 
    increment attemps greater than RECAPTCHA_ATTEMPTS.
    
    A RECAPTCHA_TOKEN is also inserted in the user's session and
    incremented.
    """
    token = RecaptchaToken.objects.filter(username=username)
    if len(token) == 0:
        token = RecaptchaToken.objects.create(username=username)
    else:
        token = token[0]

    if token.attempts <= RECAPTCHA_ATTEMPTS:
        token.attempts += 1
        token.save()
    else:
        session[RECAPTCHA_TOKEN] = RECAPTCHA_ATTEMPTS

    if RECAPTCHA_TOKEN not in session:
        session[RECAPTCHA_TOKEN] = 1
    elif session[RECAPTCHA_TOKEN] <= RECAPTCHA_ATTEMPTS:
        session[RECAPTCHA_TOKEN] = session[RECAPTCHA_TOKEN] + 1
        
def login_success(session, username):
    """
    Deletes the RECAPTCHA_TOKEN in the session if any and deletes
    the RecaptchaToken in the database if exist.
    """
    if RECAPTCHA_TOKEN in session:
        del session[RECAPTCHA_TOKEN]
    token = RecaptchaToken.objects.filter(username=username)
    if len(token) > 0:
        token[0].delete()

class RecaptchaResponse(object):
    def __init__(self, is_valid, error_code=None):
        self.is_valid = is_valid
        self.error_code = error_code

def displayhtml (public_key = RECAPTCHA_PUBLIC_KEY,
                 use_ssl = PRODUCTION_SERVER,
                 error = None):
    """Gets the HTML to display for reCAPTCHA

    public_key -- The public api key
    use_ssl -- Should the request be sent over ssl?
    error -- An error message to display (from RecaptchaResponse.error_code)"""

    error_param = ''
    if error:
        error_param = '&error=%s' % error

    if use_ssl:
        server = API_SSL_SERVER
    else:
        server = API_SERVER

    return """<script type="text/javascript" src="%(ApiServer)s/challenge?k=%(PublicKey)s%(ErrorParam)s"></script>
<noscript>
  <iframe src="%(ApiServer)s/noscript?k=%(PublicKey)s%(ErrorParam)s" height="300" width="500" frameborder="0"></iframe>
  <textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
  <input type='hidden' name='recaptcha_response_field' value='manual_challenge' />
</noscript>
""" % {
        'ApiServer' : server,
        'PublicKey' : public_key,
        'ErrorParam' : error_param,
        }


def submit (request, recaptcha_challenge_field,
            recaptcha_response_field,
            private_key = RECAPTCHA_PRIVATE_KEY):
    """
    Submits a reCAPTCHA request for verification. Returns RecaptchaResponse
    for the request

    recaptcha_challenge_field -- The value of recaptcha_challenge_field from the form
    recaptcha_response_field -- The value of recaptcha_response_field from the form
    private_key -- your reCAPTCHA private key
    X remoteip -- the user's ip address - replaced by a request object
    request -- the user's request
    """

    if not (recaptcha_response_field and recaptcha_challenge_field and
            len (recaptcha_response_field) and len (recaptcha_challenge_field)):
        return RecaptchaResponse (is_valid = False, error_code = 'incorrect-captcha-sol')
    

    def encode_if_necessary(s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return s

    params = urllib.urlencode ({
            'privatekey': encode_if_necessary(private_key),
            'remoteip' :  encode_if_necessary(get_client_ip(request)),
            'challenge':  encode_if_necessary(recaptcha_challenge_field),
            'response' :  encode_if_necessary(recaptcha_response_field),
            })

    request = urllib2.Request (
        url = "http://%s/recaptcha/api/verify" % VERIFY_SERVER,
        data = params,
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "reCAPTCHA Python"
            }
        )
    
    httpresp = urllib2.urlopen (request)

    return_values = httpresp.read ().splitlines ();
    httpresp.close();

    return_code = return_values [0]

    if (return_code == "true"):
        return RecaptchaResponse (is_valid=True)
    else:
        return RecaptchaResponse (is_valid=False, error_code = return_values [1])
