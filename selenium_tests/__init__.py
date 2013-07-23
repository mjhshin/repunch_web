from django.test import LiveServerTestCase, TestCase
from selenium.webdriver.firefox.webdriver import WebDriver

from repunch.settings import TEST_REMOTE_SERVER

class LocalTestCase(LiveServerTestCase):
    """
    Base class for testing locally.
    """
    
    @classmethod
    def setUpClass(cls):
        cls.driver = WebDriver()
        super(LocalTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(LocalTestCase, cls).tearDownClass()
        cls.driver.quit()
    
    def open(self, url):
        self.driver.get("%s%s" % (self.live_server_url, url))
        
class RemoteTestCase(TestCase):
    """
    Base class for testing the remote site.
    """
    
    SERVER_URL = "http://www.repunch.com"
    
    @classmethod
    def setUpClass(cls):
        cls.driver = WebDriver()
        super(RemoteTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(RemoteTestCase, cls).tearDownClass()
        cls.driver.quit()
    
    def open(self, url):
        self.driver.get("%s%s" % (RemoteTestCase.SERVER_URL, url))      

def get_test_case_class():
    """
    Returns the LocalTestCase if TEST_REMOTE_SERVER is False.
    RemoteTestCase otherwise.
    """
    if TEST_REMOTE_SERVER:
        return RemoteTestCase
    else:
        return LocalTestCase
