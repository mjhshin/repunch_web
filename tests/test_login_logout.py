"""
Selenium test for login and logout.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest
from parse.apps.accounts.models import Account

TEST_USER = {
    "username": "clothing",
    "password": "123456",
    "email": "vandolf@repunch.com",
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
        {'test_name': "Not having the stay signed in option "+\
            "sets the sessionid's cookie expiry to None"},
        {'test_name': "Having the stay signed in option "+\
            "sets the sessionid's cookie expiry to a number"},
        {'test_name': "Logout works"},
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
    
    ##########  Not having the stay signed in option
    ##########  sets the sessionid's cookie expiry to None
    parts[3]["success"] = test.driver.get_cookie(\
        "sessionid")['expiry'] == None
    
    ##########  Having the stay signed in option
    ##########  sets the sessionid's cookie expiry to a number
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    try:
        test.new_driver(save_session_cookie=False)
        test.find("#header-signin-btn").click() # ACTION!
        test.find("#stay_in").click() # ACTION!
        test.action_chain(1, selectors, "send_keys") # ACTION!
        sleep(7)
        parts[4]["success"] = test.driver.get_cookie(\
            "sessionid")['expiry'] != None
    except Exception as e:
        print e
    
    ##########  Logout works
    try:
        test.find("#link-logout").click() # ACTION!
        sleep(2)
        parts[5]["success"] =\
            test.is_current_url(reverse("public_home"))
    except Exception as e:
        print e
    
    ##########  Forgot password form functional
    try:
        test.find("#header-signin-btn").click() # ACTION!
        test.find("//form[@id='forgot-pass-form']/a",
            type="xpath").click() # ACTION!
        sleep(3)
        test.find("//div[@id='forgot-pass-form-div']/input[" +\
            "@name='forgot-pass-email']", type="xpath").send_keys(\
                TEST_USER['email'])
        sleep(1)
        test.find("//div[@id='forgot-pass-form-div']/input[" +\
            "@type='submit']", type="xpath").click()
        sleep(3)
        parts[6]['success'] = str(test.find(\
            "#forgot-pass-form").text) == "Password Reset form sent."
    except Exception as e:
        print e
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()

def test_login_page():
    """
    The dedicated login page.
    """
    test = SeleniumTest()
    parts = [ 
        {'test_name': "Wrong login credentials show error"},
        {'test_name': "Successful login redirects to dashboard"},
        {'test_name': "Not having the stay signed in option "+\
            "sets the sessionid's cookie expiry to None"},
        {'test_name': "Having the stay signed in option "+\
            "sets the sessionid's cookie expiry to a number"},
        {'test_name': "Logout works"},
        {'test_name': "Forgot password form functional"},
    ]
    section = {
        "section_name": "Login page working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    test.open(reverse("manage_login")) # ACTION!
    
    ##########  Wrong login credentials show error
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password'] + "sdg"),
        ("", Keys.RETURN)
    )
    try:
        test.action_chain(1, selectors, "send_keys") # ACTION!
        sleep(3)
        parts[0]["success"] =\
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
        parts[1]["success"] =\
            test.is_current_url(reverse("store_index"))
    except Exception as e:
        print e
    
    ##########  Not having the stay signed in option
    ##########  sets the sessionid's cookie expiry to None
    parts[2]["success"] = test.driver.get_cookie(\
        "sessionid")['expiry'] == None
    
    ##########  Having the stay signed in option
    ##########  sets the sessionid's cookie expiry to a number
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    try:
        test.new_driver(save_session_cookie=False)
        test.open(reverse("manage_login")) # ACTION!
        sleep(1)
        test.find("#stay_in").click() # ACTION!
        test.action_chain(1, selectors, "send_keys") # ACTION!
        sleep(7)
        parts[3]["success"] = test.driver.get_cookie(\
            "sessionid")['expiry'] != None
    except Exception as e:
        print e
    
    ##########  Logout works
    try:
        test.find("#link-logout").click() # ACTION!
        sleep(2)
        parts[4]["success"] =\
            test.is_current_url(reverse("public_home"))
    except Exception as e:
        print e
    
    ##########  Forgot password form functional
    try:
        test.open(reverse("manage_login"))
        sleep(1)
        test.find("//form[@id='forgot-pass-form']/a",
            type="xpath").click() # ACTION!
        sleep(3)
        test.find("//div[@id='forgot-pass-form-div']/input[" +\
            "@name='forgot-pass-email']", type="xpath").send_keys(\
                TEST_USER['email'])
        sleep(1)
        test.find("//div[@id='forgot-pass-form-div']/input[" +\
            "@type='submit']", type="xpath").click()
        sleep(3)
        parts[5]['success'] = str(test.find(\
            "#forgot-pass-form").text) == "Password Reset form sent."
    except Exception as e:
        print e
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()










