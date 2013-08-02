"""
Selenium tests for dashboard 'My Account' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest

TEST_USER = {
    "username": "clothing",
    "password": "123456",
}

def test_edit_store_details():
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Edit page reachable"},
        {'test_name': "Changing store name are saved to Parse"},
        {'test_name': "Changes to street are saved to Parse"},
        {'test_name': "Changes to city are saved to Parse"},
        {'test_name': "Changes to state are saved to Parse"},
        {'test_name': "Changes to zip are saved to Parse"},
        {'test_name': "Changes to phone number are saved to Parse"},
        {'test_name': "Changes to hours are saved to Parse"},
        {'test_name': "Entering invalid hours shows error"},
        {'test_name': "Entering invalid phone number shows error"},
        {'test_name': "There can be no more than 7 hours rows"},
        {'test_name': "Changes are refelcted in store details page"},
        {'test_name': "Cancel button redirects user back to store " +\
            "details page and no changes are saved to Parse"},
        {'test_name': "Clicking Add/Change Photo brings up the " +\
            "image upload dialog"},
        {'test_name': "Clicking cancel on upload removes the dialog"},
        {'test_name': "Uploading images works"},
        {'test_name': "Clicking cancel on crop removes the dialog"},
        {'test_name': "Cropping images works"},
        {'test_name': "New store avatar is saved to Parse"},
        {'test_name': "The store avatar thumbnail and image in " +\
            "store details/edit match the one saved in Parse."},
    ]
    section = {
        "section_name": "Edit store details working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page TODO
    
    
    ##########  Edit page reachable TODO
    
    ##########  Changing store name are saved to Parse TODO
    
    ##########  Changes to street are saved to Parse TODO
    
    ##########  Changes to city are saved to Parse TODO
    
    ##########  Changes to state are saved to Parse TODO
    
    ##########  Changes to zip are saved to Parse TODO
    
    ##########  Changes to phone number are saved to Parse TODO
    
    ##########  Changes to hours are saved to Parse TODO
    
    ##########  Entering invalid hours shows error TODO
    
    ##########  Entering invalid phone number shows error TODO
    
    ##########  There can be no more than 7 hours rows TODO
    
    ##########  Changes are refelcted in store details page TODO
    
    ##########  Cancel button redirects user back to store TODO
    ##########  details page and no changes are saved to Parse
    
    ##########  Clicking Add/Change Photo brings up the TODO
    ##########  image upload dialog
    
    ##########  Clicking cancel on upload removes the dialog TODO
    
    ##########  Uploading images works TODO
    
    ##########  Clicking cancel on crop removes the dialog TODO
    
    ##########  Cropping images works TODO
    
    ##########  New store avatar is saved to Parse TODO
    
    ##########  The store avatar thumbnail and image in TODO
    ##########  store details/edit match the one saved in Parse
    
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()
