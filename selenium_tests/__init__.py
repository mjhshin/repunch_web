from django.test import LiveServerTestCase, TestCase
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from repunch.settings import TEST_REMOTE_SERVER

class LocalTestCase(LiveServerTestCase):
    """
    Base class for testing locally.
    """
    
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(10)
        super(LocalTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(LocalTestCase, cls).tearDownClass()
        cls.driver.quit()
        
    def new_driver(self):
        """
        quits the current driver and instantiates a new one
        """
        self.driver.quit()
        sleep(2)
        self.driver = webdriver.Firefox()
    
    def open(self, url):
        self.driver.get("%s%s" % (self.live_server_url, url))
        
    def find(self, selector, type="css"):
        """
        Shortcut for find_element_by_css_selector or xpath, etc
        """     
        if type == "css":
            return self.driver.find_element_by_css_selector(selector)
        elif type == "xpath":
            return self.driver.find_element_by_xpath(selector)
            
    def action_chain(self, wait_time, selectors, action="click",
            type="css"):
        """
        Performs the action on each of the elements found by the
        given selectors located by the given method with the given 
        wait_time in between each action.
        
        Note that if action is send_keys, selectors must be a list 
        of tuples that contain a selector and a string.
        """
        for selector in selectors:
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
    
        
class RemoteTestCase(TestCase):
    """
    Base class for testing the remote site.
    """
    
    SERVER_URL = "http://www.repunch.com"
    
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(10)
        super(RemoteTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(RemoteTestCase, cls).tearDownClass()
        cls.driver.quit()
        
    def new_driver(self):
        """
        quits the current driver and instantiates a new one
        """
        self.driver.quit()
        sleep(2)
        self.driver = webdriver.Firefox()
    
    def open(self, url):
        self.driver.get("%s%s" % (RemoteTestCase.SERVER_URL, url)) 
        
    def find(self, selector, type="css"):
        """
        Shortcut for find_element_by_css_selector or xpath, etc
        """     
        if type == "css":
            return self.driver.find_element_by_css_selector(selector)
        elif type == "xpath":
            return self.driver.find_element_by_xpath(selector)
            
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

def get_test_case_class():
    """
    Returns the LocalTestCase if TEST_REMOTE_SERVER is False.
    RemoteTestCase otherwise.
    """
    if TEST_REMOTE_SERVER:
        return RemoteTestCase
    else:
        return LocalTestCase
