"""
Selenium tests for dashboard 'My Account' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest
from parse.apps.accounts.models import Account

TEST_USER = {
    "username": "clothing",
    "password": "123456",
}
    
    
# set the store information 
store = Account.objects().get(username=TEST_USER['username'],
    include="Store").store
    
DEFAULT_STORE_INFO = {
    "store_name": "Vandolf's Women's Clothing Corp",
    "street": "1370 Virginia Ave 4d",
    "city": "Bronx",
    "state": "NY",
    "zip": "10462",
    "phone_number": "(777) 777-7777",
    "store_description": "Beautiful clothing for women!",
    "store_timezone": "America/New_York",
    "neighborhood": "Parkchester",
    "hours": [{"close_time":"1930","day":1,"open_time":"1000"},
            {"close_time":"1930","day":2,"open_time":"1000"},
            {"close_time":"1930","day":3,"open_time":"1000"},
            {"close_time":"1930","day":4,"open_time":"1000"},
            {"close_time":"1930","day":5,"open_time":"1000"},
            {"close_time":"1930","day":6,"open_time":"1000"},
            {"close_time":"1930","day":7,"open_time":"1000"}],
    "coordinates": [40.83673, -73.862669],
}

store.update_locally(DEFAULT_STORE_INFO, False)
store.update()

TEST_STORE_INFO = {
    "store_name": "Vandolf's Military Militia",
    "street": "952 Sutter St",
    "city": " San Francisco",
    "state": "CA",
    "zip": "94109",
    "phone_number": "(111) 111-1111",
    "store_description": "Weapons so big they should be illegal.",
    "hours": [{"close_time":"1930","day":2,"open_time":"1000"},
            {"close_time":"1930","day":3,"open_time":"1000"},
            {"close_time":"1930","day":4,"open_time":"1000"},
            {"close_time":"1930","day":5,"open_time":"1000"},
            {"close_time":"1930","day":6,"open_time":"1000"},],
}

def test_edit_store_details():
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Edit page reachable"},
        {'test_name': "Changes to store name are visible"},
        {'test_name': "Changes to store name are saved to Parse"},
        {'test_name': "Changes to street are visible"},
        {'test_name': "Changes to street are saved to Parse"},
        {'test_name': "Changes to city are visible"},
        {'test_name': "Changes to city are saved to Parse"},
        {'test_name': "Changes to state are visible"},
        {'test_name': "Changes to state are saved to Parse"},
        {'test_name': "Changes to zip are visible"},
        {'test_name': "Changes to zip are saved to Parse"},
        {'test_name': "Changes to phone number are visible"},
        {'test_name': "Changes to phone number are saved to Parse"},
        {'test_name': "Changes to hours are visible"},
        {'test_name': "Changes to hours are saved to Parse"},
        {'test_name': "Entering invalid address shows error"},
        {'test_name': "Entering invalid hours shows error"},
        {'test_name': "Entering invalid phone number shows error"},
        {'test_name': "There can be no more than 7 hours rows"},
        {'test_name': "Changing the zip changes the store_timezone"},
        {'test_name': "Changing the zip changes the neighborhood"},
        {'test_name': "Changing the zip changes the coordinates"},
        {'test_name': "Changes are relected in store details page"},
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
    
    ##########  User needs to be logged in to access page
    test.open(reverse("store_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=/manage/store/")
        
    # login
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(1, selectors, "send_keys") # ACTION!
    sleep(7)
    
    ##########  Edit page reachable
    try:
        test.find("//div[@id='store-details']/a[@href='" +\
            reverse("store_edit") + "']", type="xpath").click() # ACTION!
        sleep(3)
        parts[1]['success']=test.is_curren_url(reverse("store_edit"))
    except Exception as e:
        print e
        
    ##########  Changes to store name are visible TODO
    
    ##########  Changes to store name are saved to Parse TODO
    store_name = test.find("#id_store_name")
    store_name.clear()
    store_name.send_keys(TEST_STORE_INFO['store_name'])
    test.find("#save-button").click()
    sleep(3)
    
    
    ##########  Changes to street are visible TODO
    
    ##########  Changes to street are saved to Parse TODO
    
    ##########  Changes to city are visible TODO
    
    ##########  Changes to city are saved to Parse TODO
    
    ##########  Changes to state are visible TODO
    
    ##########  Changes to state are saved to Parse TODO
    
    ##########  Changes to zip are visible TODO
    
    ##########  Changes to zip are saved to Parse TODO
    
    ##########  Changes to phone number are visible TODO
    
    ##########  Changes to phone number are saved to Parse TODO
    
    ##########  Changes to hours are visible TODO
    
    ##########  Changes to hours are saved to Parse TODO
    
    ##########  Entering invalid address shows error TODO
    
    ##########  Entering invalid hours shows error TODO
    
    ##########  Entering invalid phone number shows error TODO
    
    ##########  There can be no more than 7 hours rows TODO
    
    ##########  Changing the zip changes the store_timezone TODO
    
    ##########  Changing the zip changes the neighborhood TODO
    
    ##########  Changing the zip changes the coordinates TODO
    
    ##########  Changes are reflected in store details page TODO
    
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
