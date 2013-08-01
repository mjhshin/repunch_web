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
    "username": "clothing",
    "password": "123456",
}

def test_login_dialog():
    """
    The dialog opened by clicking business signin in all public pages.
    """
    test = SeleniumTest()
    parts = [
        {'test_name': "Login dialog showing up"},
        {'test_name': "Wrong login credentials show error"},
        {'test_name': "Successful login redirects to dashboard"},
        {'test_name': "Closing the window logs out the user if "+\
            "the stay signed in option was not activated"},
        {'test_name': "Closing the window does not log out the "+\
            " user if the stay signed in option was activated"},
        {'test_name': "Forgot password form functional"},
    ]
    section = {
        "section_name": "Login dialog working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    test.open(reverse("public_home")) # ACTION!

    ##########  Login dialog showing up
    try:
        test.find("#header-signin-btn").click() # ACTION!
        if test.find("#dialog-login").is_displayed():
            parts[0]["success"] = True
    except Exception as e:
        print e
    
    ##########  Wrong login credentials show error
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password'] + "sdg"),
        ("", Keys.RETURN)
    )
    try:
        test.action_chain(1, selectors, "send_keys") # ACTION!
        sleep(3)
        parts[1]["success"] =\
            str(test.find("#dialog-login-message").text) ==\
                "The username or password you entered is incorrect."
    except Exception as e:
        print e
        
    # clear the input fields
    test.find("#id_username").clear()
    test.find("#id_password").clear()
        
    ##########  Successful login redirects to dashboard
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    try:
        test.action_chain(1, selectors, "send_keys") # ACTION!
        sleep(7)
        parts[2]["success"] =\
            test.is_current_url(reverse("store_index"))
    except Exception as e:
        print e
    
    ##########  Closing the window logs out the user if 
    ##########  the stay signed in option was not activated.
    test.new_driver()    
    test.open(reverse("public_home")) # ACTION!
    parts[3]["success"] =\
        test.is_current_url(reverse("public_home"))
    
    ##########  Closing the window does not log out the
    ##########  user if the stay signed in was activated.
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    try:
        test.find("#header-signin-btn").click() # ACTION!
        test.find("#stay_in").click() # ACTION!
        test.action_chain(1, selectors, "send_keys") # ACTION!
        sleep(7)
        test.new_driver()
        test.open(reverse("public_home")) # ACTION!
        parts[4]["success"] =\
            test.is_current_url(reverse("store_index"))
    except Exception as e:
        print e
    
    
    
    
    
    
    
    
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()
