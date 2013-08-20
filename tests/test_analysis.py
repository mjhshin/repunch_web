"""
Selenium tests for dashboard 'Analysis' tab.
"""

from django.core.urlresolvers import reverse
from time import sleep

from tests import SeleniumTest

TEST_USER = {
    "username": "clothing",
    "password": "123456",
}

def test_trends():
    """
    Tests for trends graph.
    """
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
    ]
    section = {
        "section_name": "Analysis trends graph working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("analysis_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("analysis_index"))
        
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
    
    
def test_breakdown():
    """
    Tests for breakdown graph.
    """
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
    ]
    section = {
        "section_name": "Analysis breakdown graph working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("analysis_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("analysis_index"))
        
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
    
    
def test_reward_redemptions():
    """
    Tests for reward redemption count in the analysis page.
    """
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
    ]
    section = {
        "section_name": "Analysis reward redemptions updating?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("analysis_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("analysis_index"))
        
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
