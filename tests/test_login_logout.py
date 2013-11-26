"""
Selenium test for login and logout.

NOTE that the email is used as the username!
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest
from parse.apps.accounts.models import Account

class TestLoginDialog(SeleniumTest):
    """
    The dialog opened by clicking business signin in all public pages.
    """
    
    def __init__(self):
        super(TestLoginDialog, self).__init__()
        
        if not self.DEV_LOGIN:
            self.open(reverse("public_home"))

    def test_0(self):
        """
        Login dialog showing up
        """
        self.find("#header-signin-btn").click() 
        sleep(1)
        return self.find("#dialog-login").is_displayed();
    
    def test_1(self):
        """
        Wrong login credentials show error
        """
        selectors = (
            ("#login_username", USER['username']),
            ("#login_password", USER['password'] + "sdg"),
            ("", Keys.RETURN)
        )
        self.action_chain(0, selectors, "send_keys")
        sleep(3)
        return self.find("#dialog-login-message").text ==\
                "Incorrect email or password."
        
    def test_2(self):
        """
        Successful login redirects to dashboard
        """
        selectors = (
            ("#login_username", USER['username']),
            ("#login_password", USER['password']),
            ("", Keys.RETURN)
        )
        self.action_chain(0, selectors, "clear")
        self.action_chain(1, selectors, "send_keys")
        sleep(7)
        return self.is_current_url(reverse("store_index"))
    
    def test_3(self):
        """
        Not having the stay signed in option sets the sessionid's 
        cookie expiry to None
        """
        return self.driver.get_cookie("sessionid")['expiry'] == None
    
    def test_4(self):
        """
        Having the stay signed in option sets the sessionid's cookie
        expiry to a number
        """
        selectors = (
            ("#login_username", USER['username']),
            ("#login_password", USER['password']),
            ("", Keys.RETURN)
        )
        self.new_driver(save_session_cookie=False)
        self.find("#header-signin-btn").click() # ACTION!
        self.find("#stay_in").click() # ACTION!
        self.action_chain(0, selectors, "send_keys") # ACTION!
        sleep(7)
        success = self.driver.get_cookie(\
            "sessionid")['expiry'] != None or self.DEV_LOGIN
            
        if self.DEV_LOGIN:
            return success, "Test skipped since dev site "+\
                "always have expiry as None."
        else:
            return success
    
    def test_5(self):
        """
        Logout works
        """
        self.logout()
        if self.DEV_LOGIN:
            return self.is_current_url(reverse("manage_dev_login")+"?next=/")
        else:
            return self.is_current_url(reverse("public_home"))
    
    def test_6(self):
        """
        Forgot password form functional
        """
        self.dev_login()
        self.find("#header-signin-btn").click()
        self.find("//form[@id='forgot-pass-form']/a",
            type="xpath").click()
        sleep(1)
        self.find("//div[@id='forgot-pass-form-div']/input[" +\
            "@name='forgot-pass-email']", type="xpath").send_keys(\
                self.account.email)
        self.find("//div[@id='forgot-pass-form-div']/input[" +\
            "@type='submit']", type="xpath").click()
        sleep(5)
        return self.find("#forgot-pass-form").text ==\
            "Password Reset form sent."
    

def test_login_page():
    """
    The dedicated login page.
    """
    account = Account.objects().get(username=USER['username'])
    
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
    self.results.append(section)
    
    self.open(reverse("manage_login")) # ACTION!
    
    ##########  Wrong login credentials show error
    selectors = (
        ("#login_username", USER['username']),
        ("#login_password", USER['password'] + "sdg"),
        ("", Keys.RETURN)
    )
    try:
        self.action_chain(0, selectors, "send_keys") # ACTION!
        sleep(3)
        parts[0]["success"] =\
            str(self.find("#dialog-login-message").text) ==\
                "Incorrect email or password."
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
        
    # clear the input fields
    self.find("#login_username").clear()
    self.find("#login_password").clear()
        
    ##########  Successful login redirects to dashboard
    selectors = (
        ("#login_username", USER['username']),
        ("#login_password", USER['password']),
        ("", Keys.RETURN)
    )
    try:
        self.action_chain(0, selectors, "send_keys") # ACTION!
        sleep(7)
        parts[1]["success"] =\
            self.is_current_url(reverse("store_index"))
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
    
    ##########  Not having the stay signed in option
    ##########  sets the sessionid's cookie expiry to None
    parts[2]["success"] = self.driver.get_cookie(\
        "sessionid")['expiry'] == None
    
    ##########  Having the stay signed in option
    ##########  sets the sessionid's cookie expiry to a number
    selectors = (
        ("#login_username", USER['username']),
        ("#login_password", USER['password']),
        ("", Keys.RETURN)
    )
    try:
        self.new_driver(save_session_cookie=False)
        self.open(reverse("manage_login")) # ACTION!
        sleep(1)
        self.find("#stay_in").click() # ACTION!
        self.action_chain(0, selectors, "send_keys") # ACTION!
        sleep(7)
        
        parts[3]["success"] = self.driver.get_cookie(\
            "sessionid")['expiry'] != None or self.DEV_LOGIN
            
        if self.DEV_LOGIN:
            parts[3]['test_message'] = "Test skipped since dev site "+\
                "always have expiry as None."
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
    
    ##########  Logout works
    try:
        self.logout() # ACTION!
        sleep(2)
        if self.DEV_LOGIN:
            parts[4]["success"] =\
                self.is_current_url(reverse("manage_dev_login")+"?next=/")
        else:
            parts[4]["success"] =\
                self.is_current_url(reverse("public_home"))
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
    
    ##########  Forgot password form functional
    try:
        self.dev_login()
        self.open(reverse("manage_login"))
        sleep(1)
        self.find("//form[@id='forgot-pass-form']/a",
            type="xpath").click() # ACTION!
        sleep(3)
        self.find("//div[@id='forgot-pass-form-div']/input[" +\
            "@name='forgot-pass-email']", type="xpath").send_keys(\
                account.email)
        sleep(1)
        self.find("//div[@id='forgot-pass-form-div']/input[" +\
            "@type='submit']", type="xpath").click()
        sleep(5)
        parts[5]['success'] = str(self.find(\
            "#forgot-pass-form").text) == "Password Reset form sent."
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
    
    # END OF ALL TESTS - cleanup
    return self.tear_down()










