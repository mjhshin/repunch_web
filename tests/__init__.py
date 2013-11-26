from django.core.urlresolvers import reverse
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException,\
NoSuchElementException

from cloud_code.tests import CloudCodeTest

class SeleniumTest(CloudCodeTest):
    """
    Wrapper around selenium - makes life easier.
    """
    
    """
    Note that these tests need to be tested on the production server,
    not localhost because things that depend on the cloud code pushing
    notifications are not tested for localhost.
    """
    
    #SERVER_URL = "https://www.repunch.com"
    #SERVER_URL = "http://dev.repunch.com"
    SERVER_URL = "http://localhost:8000"
    
    DEV_LOGIN = True
    # Mail sent by sendgrid
    CHECK_SENT_MAIL = SERVER_URL !=  "https://www.repunch.com" 
    
    VERBOSE = True
    IMPLICITLY_WAIT = 10
    
    def __init__(self, fetch_user=True):
        """
        tests has the following format:
        [ {'test_name': "Test title"}, ... ]
        """
        super(SeleniumTest, self).__init__(fetch_user)
        self.driver = webdriver.Firefox()
        self.set_to_implicit_wait(True)
        self.dev_login()
        
    def set_to_implicit_wait(self, wait):
        if wait:
            self.driver.implicitly_wait(SeleniumTest.IMPLICITLY_WAIT)
        else:
            self.driver.implicitly_wait(0)
            
    def dev_login(self):
        if SeleniumTest.DEV_LOGIN:
            if not self.is_current_url(reverse("manage_dev_login")+"?next=/"):
                self.open()
                sleep(1)
                
            self.find("#username").send_keys("admin")
            self.find("#password").send_keys("vandolfisthebestandshinsucks")
            self.find("input[type='submit']").click()
            sleep(2)
        
    def get_results(self, verbose=False):
        """
        Quit the driver and return the results of the test.
        """
        results = super(SeleniumTest, self).get_results(verbose)
        self.driver.quit()
        return results
        
    def open(self, url="/"):
        self.driver.get("%s%s" % (SeleniumTest.SERVER_URL, url))
        
    def login(self, username, password, url=None, final_sleep=5):
        """ 
        This should only be used when not yet logged in! 
        If the url is provided, then this will use the dedicated login
        page. Otherwise, the login dialog is used.
        """
        if url:
            self.open(url)
            sleep(1)
        else:
            self.open(reverse("public_home"))
            sleep(1)
            self.find("#header-signin-btn").click()
            
        selectors = (
            ("#login_username", username),
            ("#login_password", password),
            ("", Keys.RETURN)
        )
        self.action_chain(0, selectors, "send_keys")
        sleep(final_sleep) 
    
    def logout(self):
        self.open(reverse("manage_logout"))
        sleep(2)
   
    def is_current_url(self, url):
        """
        returns True if the current url is equal to url 
        """
        return self.driver.current_url == SeleniumTest.SERVER_URL+url
    
    def new_driver(self, save_session_cookie=True):
        """
        Quits the current driver and instantiates a new one.
        
        If save_session_cookie is True saves the current cookies and 
        loads it back after getting back to the SERVER_URL page 
        (which is necessary in order to use add_cookie).
        """
        if save_session_cookie:
            cookie = self.driver.get_cookie("sessionid")
        self.driver.quit()
        sleep(2)
        self.driver = webdriver.Firefox()
        if not SeleniumTest.DEV_LOGIN:
            self.open()    
            sleep(1)
        self.dev_login()    
        if save_session_cookie and cookie:
            self.driver.add_cookie(cookie)
            
    def switch_to_alert(self):
        """
        Returns the active alert if one is present. Otherwise None.
        """
        alert = self.driver.switch_to_alert()
        try:
            # switch_to_alert is actually lazy - it returns a
            # web element even if an alert is not present
            alert.text # this will check if the alert actually exist
        except NoAlertPresentException:
            return None
        else:
            return alert
        
    def find(self, selector, type="css", multiple=False):
        """
        Shortcut for find_element_by_css_selector(s) or xpath, etc
        """     
        if type == "css":
            if multiple:
                return self.driver.find_elements_by_css_selector(selector)
            else:
                return self.driver.find_element_by_css_selector(selector)
        elif type == "xpath":
            if multiple:
                return self.driver.find_elements_by_xpath(selector)
            else:
                return self.driver.find_element_by_xpath(selector)
        elif type == "tag_name":
            if multiple:
                return self.driver.find_elements_by_tag_name(selector)
            else:
                return self.driver.find_element_by_tag_name(selector)
                
    def get_selected(self, selector, type="css"):
        """
        Returns the selected option element from the select.
        The selectore must select option tags.
        
        Depracated. Don't use this.
        """
        els = self.find(selector, type=type, multiple=True)
        for el in els:
            if el.is_selected():
                return el
                
    def element_exists(self, selector, type="css"):
        """ Checks if an element exists with no implicit wait """
        self.driver.implicitly_wait(0)
        exists = False
        try:
            exists = self.find(selector, type) is not None
        except NoSuchElementException:
            pass
            
        self.driver.implicitly_wait(SeleniumTest.IMPLICITLY_WAIT)
        return exists
            
    def action_chain(self, wait_time, selectors, action="click",
            type="css"):
        """
        Performs the action on each of the elements found by the
        given selectors located by the given method with the given 
        wait_time in between each action.
        
        Note that if action is send_keys, selectors must be a list 
        of tuples that contain a selector and a string. If a selector
        is not provided then an ActionChains will be performed at
        the current element.
        """
        for selector in selectors:
            if wait_time > 0:
                sleep(wait_time)
            if action == "click":
                self.find(selector, type).click()
            elif action == "move":
                ActionChains(self.driver).move_to_element(\
                    self.find(selector, type)).perform()
            elif action == "send_keys":
                if len(selector[0]) == 0:
                    ActionChains(self.driver).send_keys(\
                        selector[1]).perform()
                else:
                    self.find(selector[0],type).send_keys(selector[1])
            elif action == "clear":
                if self._type(selector) in (tuple, list):
                    if len(selector[0]) > 0:
                        self.find(selector[0], type).clear()
                else:
                    if len(selector) > 0:
                        self.find(selector, type).clear()
                    
    def _type(self, obj):
        """
        Simply returns the type of an object. This is here because
        type is rebound to a string in all functions.
        """
        return type(obj)
        
    def fields_required(self, selectors, init_func,
        test_offset=0, type="css"):
        """
        Generates tests for each selector.
        The selectors is a tuple (selector, __doc__)
        
        Calls init_func first, which should return True.
        """
        for i, sel in enumerate(selectors):
            if i == 0:
                func = lambda: init_func() and\
                    self.field_required(sel[0], type)
            else:
                func = lambda: self.field_required(sel[0], type)
                
            func.__doc__ = sel[1]
            setattr(self, "test_%d" % (i+test_offset,), func)
        
    def field_required(self, selector, type="css"):
        return self.find(selector, type).text ==\
            "This field is required."
            
            
            
            
            
            
            
