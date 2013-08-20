"""
Selenium tests for dashboard 'Workbench' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest

TEST_USER = {
    "username": "clothing",
    "password": "123456",
}

def test_punch():
    """
    Tests for punch customers section of the workbench.
    """
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
    ]
    section = {
        "section_name": "Workbench page punching working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("workbench_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("workbench_index"))
        
    # login
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(5) 
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
    
def test_redemptions():
    """
    Tests for redemptions section of the workbench.
    """
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
    ]
    section = {
        "section_name": "Workbench page redemption working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("workbench_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("workbench_index"))
        
    # login
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(5) 
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
