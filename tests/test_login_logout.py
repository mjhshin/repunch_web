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
            ("#login_username", self.USER['username']),
            ("#login_password", self.USER['password'] + "sdg"),
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
            ("#login_username", self.USER['username']),
            ("#login_password", self.USER['password']),
            ("", Keys.RETURN)
        )
        self.action_chain(0, selectors, "clear")
        self.action_chain(0, selectors, "send_keys")
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
            ("#login_username", self.USER['username']),
            ("#login_password", self.USER['password']),
            ("", Keys.RETURN)
        )
        self.new_driver(save_session_cookie=False)
        self.find("#header-signin-btn").click() 
        sleep(1)
        self.find("#stay_in").click() 
        self.action_chain(0, selectors, "send_keys") 
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
    

class TestLoginPage(SeleniumTest):
    """
    The dedicated login page.
    """
    
    def __init__(self):
        super(TestLoginPage, self).__init__()

        self.open(reverse("manage_login"))
    
    def test_0(self):
        """
        Wrong login credentials show error
        """
        selectors = (
            ("#login_username", self.USER['username']),
            ("#login_password", self.USER['password'] + "sdg"),
            ("", Keys.RETURN)
        )
        self.action_chain(0, selectors, "send_keys") 
        sleep(3)
        return self.find("#dialog-login-message").text ==\
                "Incorrect email or password."
        
    def test_1(self):
        """
        Successful login redirects to dashboard
        """
        selectors = (
            ("#login_username", self.USER['username']),
            ("#login_password", self.USER['password']),
            ("", Keys.RETURN)
        )
        self.action_chain(0, selectors, "clear") 
        self.action_chain(0, selectors, "send_keys") 
        sleep(7)
        return self.is_current_url(reverse("store_index"))

    def test_2(self):
        """
        Not having the stay signed in option sets the sessionid's 
        cookie expiry to None
        """
        return self.driver.get_cookie("sessionid")['expiry'] == None
    
    def test_3(self):
        """
        Having the stay signed in option sets the sessionid's 
        cookie expiry to a number
        """
        selectors = (
            ("#login_username", self.USER['username']),
            ("#login_password", self.USER['password']),
            ("", Keys.RETURN)
        )
        self.new_driver(save_session_cookie=False)
        self.open(reverse("manage_login")) 
        sleep(1)
        self.find("#stay_in").click() 
        self.action_chain(0, selectors, "send_keys") 
        sleep(7)
        
        success = self.driver.get_cookie(\
            "sessionid")['expiry'] != None or self.DEV_LOGIN
            
        if self.DEV_LOGIN:
            return success, "Test skipped since dev site "+\
                "always have expiry as None."
        else:
            return success
    
    def test_4(self):
        """
        Logout works
        """
        self.logout() 
        sleep(2)
        if self.DEV_LOGIN:
            return self.is_current_url(reverse("manage_dev_login")+"?next=/")
        else:
            return self.is_current_url(reverse("public_home"))
    
    def test_5(self):
        """
        Forgot password form functional
        """
        self.dev_login()
        self.open(reverse("manage_login"))
        sleep(1)
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
            
