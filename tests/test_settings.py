"""
Selenium tests for dashboard 'Settings' tab.
"""

from django.core.urlresolvers import reverse
from time import sleep

from tests import SeleniumTest


TEST_USER = {
    "username": "clothing",
    "password": "123456",
}

def test_settings():
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Punches employee is required"},
        {'test_name': "Punches facebook is required"},
        {'test_name': "Punches employee must be a number greater" +\
            " than 0"},
        {'test_name': "Punches facebook must be a number greater" +\
            " than 0"},
        {'test_name': "Retailer PIN is refreshable"},
        {'test_name': "Changes to Retailer PIN is immediately " +\
            "commited to Parse without having to save settings."},
        {'test_name': "Clicking cancel changes will not undo the " +\
            "change made to Retailer PIN"},
        {'test_name': "Clicking cancel changes will not save " +\
            "changes to punches facebook and punches employee"},
    ]
    section = {
        "section_name": "Settings page working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("account_settings")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("account_setting"))
        
    # login
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(5) 
    
    
    ##########  Punches employee is required TODO
    ##########  Punches facebook is required
    ##########  Punches employee must be a number greater than 0
    ##########  Punches facebook must be a number greater than 0 TODO
    ##########  Retailer PIN is refreshable TODO
    ##########  Changes to Retailer PIN is immediately TODO
    ###         commited to Parse without having to save settings
    ##########  Clicking cancel changes will not undo the  TODO
    ###         change made to Retailer PIN
    ##########  Clicking cancel changes will not save  TODO
    ###         changes to punches facebook and punches employee
    
    
    
    
    
    
    
    
    
    
    
    # END OF ALL TESTS - cleanup
    mail.logout()
    return test.tear_down() 
