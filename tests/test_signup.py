"""
Selenium test for signup.

I know that this is not how tests are done in Django. 
The justification for this is that we are not using Django Models but
Parse Objects and services so yea.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest
from parse.apps.accounts.models import Account
# from parse.apps.stores.models import Store

TEST_USER = {
    "username": "iusluixylusr",
    "email": "admin@repunch.com",
}

def test_signup():
    test = SeleniumTest()
    parts = [
        {'test_name': "Sign up page navigable"},
        {'test_name': "Form submission okay"},
        {'test_name': "User object created"},
        {'test_name': "Store object created"},
        {'test_name': "Subscription object created"},
        {'test_name': "Settings object created"},
    ]
    section = {
        "section_name": "Sign up working properly?",
        "parts": parts,
    }
    test.results.append(section)

    ##########  Sign up page navigable
    test.open(reverse("public_signup")) # ACTION!
    parts[0]['success'] = True
    sleep(1)
    
    ##########  Form submission okay
    selectors = (
        ("#id_store_name", "test business"),
        ("#id_street", "1370 virginia ave 4d"),
        ("#id_city", "bronx"),
        ("#id_state", "ny"),
        ("#id_zip", "10462"),
        ("#categories", "baker"),
        ("", Keys.ARROW_DOWN),
        ("", Keys.RETURN),
        ("#categories", "fitn"),
        ("", Keys.ARROW_DOWN),
        ("", Keys.RETURN),
        ("#id_first_name", "Testee"),
        ("#id_last_name", "Bestee"),
        ("#Ph1", "777"),
        ("#Ph2", "777"),
        ("#Ph3", "7777"),
        ("#id_email", TEST_USER['email']),
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['username']),
        ("#id_confirm_password", TEST_USER['username']),
    )
    try:
        test.action_chain(1, selectors, action="send_keys") # ACTION!
        # ToS and submit
        selectors = (
            "#id_recurring",
            # "#signup-form-submit",
        )
        test.action_chain(2, selectors) # ACTION!
    except Exception:
        pass
    else:
        parts[1]['success'] = True
        sleep(1)

    ##########  User object created
    user = Account.objects().get(username=TEST_USER['username'])
    parts[2]['success'] = user is not None
    ##########  Store object created
    store = user.get("store")
    parts[3]['success'] = store is not None
    ##########  Subscription object created
    subscription = store.get("subscription")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    # END OF ALL TESTS
    return test.tear_down()
