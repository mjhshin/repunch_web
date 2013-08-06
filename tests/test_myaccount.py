"""
Selenium tests for dashboard 'My Account' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep
import math

from tests import SeleniumTest
from parse.apps.accounts.models import Account

TEST_USER = {
    "username": "clothing",
    "password": "123456",
    "email": "clothing@vandolf.com",
}

TEST_USER_INFO = {
    "email": "militia@vandolf.com",
}
    
    
# set the store information
account =  Account.objects().get(username=TEST_USER['username'],
    include="Store")
store = account.store
    
STORE_INFO = {
    "store_name": "Vandolf's Women's Clothing Corp",
    "street": "1370 Virginia Ave 4d",
    "city": "Bronx",
    "state": "NY",
    "zip": "10462",
    "phone_number": "(777) 777-7777",
    "store_description": "Beautiful clothing for women!",
    "hours": [],
    "store_timezone": "America/New_York",
    "neighborhood": "Parkchester",
    "coordinates": [40.83673, -73.862669],
}

store.update_locally(STORE_INFO, False)
store.update()

TEST_STORE_INFO = {
    "store_name": "Vandolf's Military Militia",
    "street": "952 Sutter St",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94109",
    "phone_number": "(111) 111-1111",
    "store_description": "Weapons so big they should be illegal.",
    "hours": [{"close_time":"0100","day":2,"open_time":"0030"},
            {"close_time":"0200","day":3,"open_time":"0130"},
            {"close_time":"0300","day":4,"open_time":"0230"},
            {"close_time":"0400","day":5,"open_time":"0330"},
            {"close_time":"0500","day":6,"open_time":"0430"},],
    "Ph1": '111', "Ph2": '111', "Ph3": '1111',
    "store_timezone": "America/Los_Angeles",
    "neighborhood": "Lower Nob Hill",
    "coordinates": [37.788366, -122.4161347],
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
        {'test_name': "Changes to email are visible"},
        {'test_name': "Changes to email are saved to Parse"},
        {'test_name': "Changes to hours are visible"},
        {'test_name': "Changes to hours are saved to Parse"},
        {'test_name': "Changing the zip changes the store_timezone"},
        {'test_name': "Changing the zip changes the neighborhood"},
        {'test_name': "Changing the zip changes the coordinates"},
        {'test_name': "Entering invalid address shows error"},
        {'test_name': "Entering invalid hours with same open time" +\
            " as close time shows error"},
        {'test_name': "Entering invalid hours with later open time" +\
            " than close time shows error"},
        {'test_name': "Having no hours is allowed"},
        {'test_name': "There can be no more than 7 hours rows"},
        # TODO fields required
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
        {'test_name': "Old store avatar is deleted from Parse files"},
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
    
    def click_store_edit():
        test.find("//div[@id='store-details']/a[@href='" +\
            reverse("store_edit") + "']", type="xpath").click() 
    
    ##########  Edit page reachable
    try:
        click_store_edit() # ACTION!
        sleep(3)
        parts[1]['success']=test.is_current_url(reverse("store_edit"))
    except Exception as e:
        print e
        
    ### make all the changes
    # store_name
    store_name = test.find("#id_store_name")
    store_name.clear()
    store_name.send_keys(TEST_STORE_INFO['store_name'])
    # street
    street = test.find("#id_street")
    street.clear()
    street.send_keys(TEST_STORE_INFO['street'])
    # city
    city = test.find("#id_city")
    city.clear()
    city.send_keys(TEST_STORE_INFO['city'])
    # state
    state = test.find("#id_state")
    state.clear()
    state.send_keys(TEST_STORE_INFO['state'])
    # zip
    zip = test.find("#id_zip")
    zip.clear()
    zip.send_keys(TEST_STORE_INFO['zip'])
    # phone_number
    ph1 = test.find("#Ph1")
    ph2 = test.find("#Ph2")
    ph3 = test.find("#Ph3")
    ph1.clear()
    ph2.clear()
    ph3.clear()
    ph1.send_keys(TEST_STORE_INFO['Ph1'])
    ph2.send_keys(TEST_STORE_INFO['Ph2'])
    ph3.send_keys(TEST_STORE_INFO['Ph3'])
    # email
    email = test.find("#id_email")
    email.clear()
    email.send_keys(TEST_USER_INFO['email'])
    # store_description
    store_description = test.find("#id_store_description")
    store_description.clear()
    store_description.send_keys(TEST_STORE_INFO['store_description'])
    # hours
    """
    {"close_time":"0100","day":2,"open_time":"0030"},
    {"close_time":"0200","day":3,"open_time":"0130"},
    {"close_time":"0300","day":4,"open_time":"0230"},
    {"close_time":"0400","day":5,"open_time":"0330"},
    {"close_time":"0500","day":6,"open_time":"0430"},
    """
    for i in range(4):
        istr = str(i)
        if i == 0:
            prefix = "id_" # rows generated by django start with id_
        else:
            prefix = "" # store_edit.js shinanigans
            
        test.find("//ul[@id='hours-{0}-row']/".format(istr) +\
            "li[@class='days']/div[{0}]".format(str(i+2)),
            type="xpath").click()
        sleep(1)
        test.find("//select[@id='{0}hours".format(prefix) + 
            "-{0}-open']".format(istr) +\
            "/option[@value='{0}:30:00']".format(istr),
            type="xpath").click()
        sleep(1)
        test.find("//select[@id='{0}hours".format(prefix) +\
            "-{0}-close']".format(istr) +\
            "/option[@value='{0}:00:00']".format(str(int(istr) + 1)),
            type="xpath").click()
        sleep(1)
        test.find("#hours-%s-add" % (istr,)).click()
        
    # store the hours preview for comparison
    hours_prev = test.find("#store-hours-preview").text.split("\n")
    
    # save!
    test.find("#save-button").click()
    sleep(6)
    
    address = str(test.find("#address p").text).split("\n")
    street = address[0]
    l2 = address[1].split(", ")
    city = l2[0]
    state, zip = l2[1].split(" ")
    phone_number = address[2]
    email = address[3]

    ##########  Changes to store name are visible 
    parts[2]['success'] = str(test.find("#address span").text) ==\
        TEST_STORE_INFO['store_name']
    
    ##########  Changes to store name are saved to Parse 
    store.store_name = None
    parts[3]['success'] = store.get("store_name") ==\
        TEST_STORE_INFO['store_name']
        
    ##########  Changes to street are visible
    parts[4]['success'] = street == TEST_STORE_INFO['street']
    
    ##########  Changes to street are saved to Parse
    store.street = None
    parts[5]['success'] = store.get("street") ==\
        TEST_STORE_INFO['street']
            
    ##########  Changes to city are visible
    parts[6]['success'] = city == TEST_STORE_INFO['city']
    
    ##########  Changes to city are saved to Parse
    store.city = None
    parts[7]['success'] = store.get("city") == TEST_STORE_INFO['city']
    
    ##########  Changes to state are visible
    parts[8]['success'] = state == TEST_STORE_INFO['state']
    
    ##########  Changes to state are saved to Parse
    store.state = None
    parts[9]['success'] = store.get("state") ==\
        TEST_STORE_INFO['state']
    
    ##########  Changes to zip are visible
    parts[10]['success'] = zip == TEST_STORE_INFO['zip']
    
    ##########  Changes to zip are saved to Parse
    store.zip = None
    parts[11]['success'] = store.get("zip") == TEST_STORE_INFO['zip']
    
    ##########  Changes to phone number are visible
    parts[12]['success'] = phone_number ==\
        TEST_STORE_INFO['phone_number']
    
    ##########  Changes to phone number are saved to Parse
    store.phone_number = None
    parts[13]['success'] = store.get("phone_number") ==\
        TEST_STORE_INFO['phone_number']
    
    ##########  Changes to email are visible
    parts[14]['success'] = email == TEST_USER_INFO['email']
    
    ##########  Changes to email are saved to Parse
    account.email = None
    parts[15]['success'] = account.get("email") ==\
        TEST_USER_INFO['email']
    
    ##########  Changes to hours are visible
    hours = test.find("#hours").text.split("\n")[1:]
    equal = True
    for hour in hours:
        success = False
        for hour_prev in hours_prev:
            if hour == hour_prev:
                success = True
                break
        if not success:
            equal = False
            break
    parts[16]['success'] = equal
    
    ##########  Changes to hours are saved to Parse
    store.hours, equal = None, True
    hours = store.get("hours")
    for hour in hours:
        success = False
        for hour_prev in TEST_STORE_INFO['hours']:
            if hour == hour_prev:
                success = True
                break
        if not success:
            equal = False
            break
    parts[17]['success'] = equal
    
    ##########  Changing the zip changes the store_timezone
    store.store_timezone = None
    parts[18]['success'] = store.get("store_timezone") ==\
        TEST_STORE_INFO['store_timezone']
    
    ##########  Changing the zip changes the neighborhood 
    store.neighborhood = None
    parts[19]['success'] = store.get("neighborhood") ==\
        TEST_STORE_INFO['neighborhood']
    
    ##########  Changing the zip changes the coordinates 
    store.coordinates = None
    parts[20]['success'] =\
        int(math.floor(store.get("coordinates")[0])) ==\
        int(math.floor(TEST_STORE_INFO['coordinates'][0])) and\
        int(math.floor(store.get("coordinates")[1])) ==\
        int(math.floor(TEST_STORE_INFO['coordinates'][1]))
    
    ##########  Entering invalid address shows error
    try:
        click_store_edit()
        sleep(3)
        # street
        street = test.find("#id_street")
        street.clear()
        street.send_keys("988 dsgsd s")
        # city
        city = test.find("#id_city")
        city.clear()
        city.send_keys("mandarin")
        # state
        state = test.find("#id_state")
        state.clear()
        state.send_keys("klk")
        # zip
        zip = test.find("#id_zip")
        zip.clear()
        zip.send_keys("941091")
        # save!
        test.find("#save-button").click()
        sleep(3)
        parts[21]['success'] = str(test.find(".errorlist").text) ==\
            "Enter a valid adress, city, state, and/or zip."
            
        test.find("//div[@id='edit-store-options']/a[2]",
            type="xpath").click()
        sleep(2)
    except Exception as e:
        print e
        parts[21]['test_message'] = str(e)
    
    ##########  Entering invalid hours with same open time
    ##########  as close time shows error
    try:
        click_store_edit()
        sleep(3)
        test.find("//select[@id='id_hours-0-open']"+\
            "/option[@value='6:30:00']", type="xpath").click()
        sleep(1)
        test.find("//select[@id='id_hours-0-close']"+\
            "/option[@value='6:30:00']", type="xpath").click()
        # save!
        test.find("#save-button").click()
        sleep(3)
        parts[22]['success'] = str(test.find(\
            ".notification div").text) == "Invalid hours. Open " +\
                "time must be greater than close time."
    except Exception as e:
        print e
        parts[22]['test_message'] = str(e)
    
    
    ##########  Entering invalid hours with later open time
    ##########  than close time shows error
    try:
        test.find("//select[@id='id_hours-0-open']"+\
            "/option[@value='6:30:00']", type="xpath").click()
        sleep(1)
        test.find("//select[@id='id_hours-0-close']"+\
            "/option[@value='5:30:00']", type="xpath").click()
        # save!
        test.find("#save-button").click()
        sleep(3)
        parts[23]['success'] = str(test.find(\
            ".notification div").text) == "Invalid hours. Open " +\
                "time must be greater than close time."
    except Exception as e:
        print e
        parts[23]['test_message'] = str(e)
    
    ##########  Having no hours is allowed
    try:
        for i in range(1, 4):
            test.find("#hours-%s-remove" % (str(i),)).click()
            sleep(1)
            test.driver.switch_to_alert().accept()
        # cannot remove the first row so just deactivate the day
        test.find("//ul[@id='hours-0-row']/" +\
            "li[@class='days']/div[2]", type="xpath").click()
        # save!
        test.find("#save-button").click()
        sleep(6)
        store.hours = None
        parts[24]['success'] =\
            test.is_current_url(reverse("store_index")) and\
            test.find("#hours").text.split("\n")[1] ==\
            'Closed Sunday - Saturday' and\
            len(store.get("hours")) == 0
    except Exception as e:
        print e
        parts[24]['test_message'] = str(e)
    
    ##########  There can be no more than 7 hours rows 
    try:
        click_store_edit()
        sleep(3)
        test.action_chain(1, ["#hours-0-add" for i in range(9)])
        # 8 because of the hidden clone row
        parts[25]['test_message'] =\
            len(test.find(".days", multiple=True)) == 8
    except Exception as e:
        print e
        parts[25]['test_message'] = str(e)
    
    
    # TODO fields required
    
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
