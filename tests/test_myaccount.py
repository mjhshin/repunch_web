"""
Selenium tests for dashboard 'My Account' tab.
"""

from django.utils import timezone
from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from dateutil.tz import tzutc
from datetime import datetime
from time import sleep
import math, requests

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

IMAGE_UPLOAD = "/home/vestrel00/Pictures/wallpapers/test.png"
    
    
# set the store information
account =  Account.objects().get(username=TEST_USER['username'],
    include="Store.Subscription")
store = account.store
subscription = store.subscription

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

SUBSCRIPTION_INFO = {
    "first_name": "Vandolf",
    "last_name": "Estrellado",
    "cc_number": None,
    "date_cc_expiration": None,
    "address": "1370 Virginia Ave 4d",
    "city": "Bronx",
    "state": "NY",
    "zip": "10462",
    "pp_cc_id": None,
    "date_pp_valid": None, 
}

subscription.update_locally(SUBSCRIPTION_INFO, False)
subscription.update()

TEST_SUBSCRIPTION_INFO = {
    "first_name": "Gundam",
    "last_name": "Wing",
    "cc_number": "4158740018304009",
    "date_cc_expiration": timezone.make_aware(\
        datetime(year=2015, month=12, day=1), tzutc()),
    "address": "123 Bleeker Street",
    "city": "Brooklyn",
    "state": "NY",
    "zip": "11571",
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
        {'test_name': "Store name is required"},
        {'test_name': "Street is required"},
        {'test_name': "City is required"},
        {'test_name': "State is required"},
        {'test_name': "Zip is required"},
        {'test_name': "Phone number is required"},
        {'test_name': "Email is required"},
        {'test_name': "Description is required"},
        {'test_name': "Cancel button redirects user back to store " +\
            "details page and no changes are saved to Parse"},
        {'test_name': "Clicking Add/Change Photo brings up the " +\
            "image upload dialog"},
        {'test_name': "Clicking cancel on upload removes the dialog"},
        {'test_name': "Clicking upload when no file is " +\
            "selected shows alert"},
        {'test_name': "Uploading images works"},
        {'test_name': "Clicking cancel on crop removes the dialog"},
        {'test_name': "Cropping images works"},
        {'test_name': "New store avatar is saved to Parse"},
        {'test_name': "Old store avatar is deleted from Parse files"},
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
    ########    as close time shows error
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
    ########    than close time shows error
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
            str(test.find("#hours").text.split("\n")[1]) ==\
            'Closed Sunday - Saturday' and\
            len(store.get("hours")) == 0
    except Exception as e:
        print e
        parts[24]['test_message'] = str(e)
    
    ##########  There can be no more than 7 hours rows 
    try:
        click_store_edit()
        sleep(3)
        test.action_chain(1, ["#hours-0-add" for i in range(10)])
        sleep(1)
        # 8 because of the hidden clone row
        parts[25]['success'] =\
            len(test.find(".days", multiple=True)) == 8
    except Exception as e:
        print e
        parts[25]['test_message'] = str(e)
    
    ## fields required
    selectors = [
        "#id_store_name", "#id_street", "#id_city",
        "#id_state", "#id_zip",
        "#Ph1", "#Ph2", "#Ph3",
        "#id_email", "#id_store_description",
    ]
    test.action_chain(0, selectors, action="clear") # ACTION!
    for i in range(len(selectors)):
        selectors[i] = (selectors[i], "   ")
    test.action_chain(0, selectors, action="send_keys") # ACTION!
    # submit
    test.find("#save-button").click() # ACTION!
    sleep(3)
    
    ##########  Store name is required 
    ##########  Street is required 
    ##########  City is required 
    ##########  State is required 
    ##########  Zip is required 
    ##########  Phone number is required 
    ##########  Email is required 
    ##########  Description is required 
    e_list = ["store_name", "street", "city", "state", "zip",
                "phone_number", "email", "store_description"]
    for i in range(26, 34):
        selector = "#%s_e ul li" % (e_list.pop(0),)
        parts[i]['success'] = str(test.find(selector).text) ==\
            "This field is required."
    
    ##########  Cancel button redirects user back to store index
    try:
        test.find("//div[@id='edit-store-options']/a[2]",
            type="xpath").click()
        sleep(2)
        parts[34]['success'] =\
            test.is_current_url(reverse('store_index'))
    except Exception as e:
        print e
        parts[34]['message'] = str(e)
    
    ##########  Clicking Add/Change Photo brings up the
    ########    image upload dialog/frame
    try:
        click_store_edit()
        sleep(3)
        test.find("#upload-avatar").click()
        sleep(1)
        # switch to frame!
        test.driver.switch_to_frame(\
            test.find("iframe", type='tag_name'))
        
        parts[35]['success'] =\
            test.find("#edit-avatar-options").is_displayed()
    except Exception as e:
        print e
        parts[35]['message'] = str(e)
    
    ##########  Clicking cancel on upload removes the dialog /frame
    try:
        test.find("//div[@id='edit-avatar-options']/a[2]",
            type="xpath").click()
        sleep(1)
        parts[36]['success'] =\
            test.find("#edit-store-options") is not None
    except Exception as e:
        print e
        parts[36]['message'] = str(e)
        
    ##########  Clicking upload when no file is selected shows alert
    try:
        test.find("#upload-avatar").click()
        sleep(1)
        # switch to frame!
        test.driver.switch_to_frame(\
            test.find("iframe", type='tag_name'))
        test.find("#upload-btn").click()
        sleep(1)
        alert = test.switch_to_alert()
        parts[37]['success'] = str(alert.text) ==\
            "Please select an image to upload."
        alert.accept()
    except Exception as e:
        print e
        parts[37]['message'] = str(e)
    
    ##########  Uploading images works
    try:
        test.find("#id_image").send_keys(IMAGE_UPLOAD)
        test.find("#upload-btn").click()
        sleep(3)
        parts[38]['success'] = test.find("#crop-btn").is_displayed()
    except Exception as e:
        print e
        parts[38]['message'] = str(e)
    
    ##########  Clicking cancel on crop removes the dialog
    try:
        test.find("//div[@id='edit-avatar-options']/a[2]",
            type="xpath").click()
        sleep(1)
        parts[39]['success'] =\
            test.find("#edit-store-options") is not None
    except Exception as e:
        print e
        parts[39]['message'] = str(e)
        
    ##########  Cropping images works
    try:
        test.find("#upload-avatar").click()
        sleep(1)
        # switch to frame!
        test.driver.switch_to_frame(\
            test.find("iframe", type='tag_name'))
        test.find("#id_image").send_keys(IMAGE_UPLOAD)
        test.find("#upload-btn").click()
        sleep(3)
        test.find("#crop-btn").click()
        parts[40]['success'] = True
    except Exception as e:
        print e
        parts[40]['message'] = str(e)
    
    sleep(5)
    old_avatar_url = store.store_avatar_url
    store.store_avatar = None
    store.store_avatar_url = None
    new_avatar_url = store.get("store_avatar_url")
    
    ##########  New store avatar is saved to Parse
    parts[41]['success'] = old_avatar_url != new_avatar_url
    
    ##########  Old store avatar is deleted from Parse files
    resp = requests.get(old_avatar_url)
    parts[42]['success'] = not resp.ok and resp.status_code == 403
    
    ##########  The store avatar thumbnail and image in
    ##########  store details/edit match the one saved in Parse
    parts[43]['success'] = new_avatar_url ==\
        test.find("#store_avatar").get_attribute("src") and\
        new_avatar_url ==\
        test.find("#avatar-thumbnail").get_attribute("src")
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()
    
    
def test_edit_account():
    # TODO test place_order
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Update account page reachable"},
        {'test_name': "Changes to first name are visible"},
        {'test_name': "Changes to first name are saved to parse"},
        {'test_name': "Changes to last name are visible"},
        {'test_name': "Changes to last name are saved to parse"},
        {'test_name': "Changes to card number are visible"},
        {'test_name': "Changes to card number are saved to parse"},
        {'test_name': "A paypal credit card id is generated & saved"},
        {'test_name': "Changes to cc expiration are visible"},
        {'test_name': "Changes to cc expiration are saved to parse"},
        {'test_name': "Changes to address are visible"},
        {'test_name': "Changes to address are saved to parse"},
        {'test_name': "Changes to city are visible"},
        {'test_name': "Changes to city are saved to parse"},
        {'test_name': "Changes to state are visible"},
        {'test_name': "Changes to state are saved to parse"},
        {'test_name': "Changes to zip are visible"},
        {'test_name': "Changes to zip are saved to parse"},
        {'test_name': "First name is required"},
        {'test_name': "Last name is required"},
        {'test_name': "Card number is required"},
        {'test_name': "Security code (cvc) is required"},
        {'test_name': "Address is required"},
        {'test_name': "City is required"},
        {'test_name': "State is required"},
        {'test_name': "Zip is required"},
        {'test_name': "ToS checked is required"},
        {'test_name': "Invalid credit card number shows error"},
        {'test_name': "Past expiration date is invalid"},
        {'test_name': "Only the last 4 digits of the card number" +\
            " is shown"},
        {'test_name': "Not changing the card number does not " +\
            "generate new paypal credit card id"},
        # TODO cancel my account
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
   
    ##########  Update account page reachable
    try:
        test.find("//div[@id='account-options']/a[1]",
            type="xpath").click()
        sleep(3)
        parts[1]['success'] =\
            test.is_current_url(reverse("account_update"))
    except Exception as e:
        print e
        parts[1]['message'] = str(e)
    
    ## Make changes
    # first clear all inputs
    for el in test.find("input[type='text']", multiple=True):
        el.clear()
    
    selectors = (
        ("#id_first_name", TEST_SUBSCRIPTION_INFO['first_name']), 
        ("#id_last_name", TEST_SUBSCRIPTION_INFO['last_name']), 
        ("#id_cc_number", TEST_SUBSCRIPTION_INFO['cc_number']),
        ("#id_cc_cvv", "905"), 
        ("#id_address", TEST_SUBSCRIPTION_INFO['address']), 
        ("#id_city", TEST_SUBSCRIPTION_INFO['city']), 
        ("#id_state", TEST_SUBSCRIPTION_INFO['state']), 
        ("#id_zip", TEST_SUBSCRIPTION_INFO['zip']),
    )
    test.action_chain(0, selectors, action="send_keys")
    month_el =\
        test.find("//select[@id='id_date_cc_expiration_month']/" +\
            "option[@value='%s']" % (str(TEST_SUBSCRIPTION_INFO[\
                'date_cc_expiration'].month)), type="xpath")
    year_el =\
        test.find("//select[@id='id_date_cc_expiration_year']/" +\
            "option[@value='%s']" % (str(TEST_SUBSCRIPTION_INFO[\
                'date_cc_expiration'].year)), type="xpath")
    month = month_el.get_attribute("value")
    year = year_el.get_attribute("value")
    month_el.click()
    year_el.click()
    
    test.find("#id_recurring").click()
    test.find("#upgrade-form-submit").click()
    sleep(5)
    
    # back to update account page
    test.find("//div[@id='account-options']/a[1]",
        type="xpath").click()
    sleep(3)
    
    ##########  Changes to first name are visible
    parts[2]['success'] =\
        test.find("#id_first_name").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['first_name']
    ##########  Changes to first name are saved to parse
    subscription.first_name = None
    parts[3]['success'] = subscription.get("first_name") ==\
        TEST_SUBSCRIPTION_INFO['first_name']
    ##########  Changes to last name are visible
    parts[4]['success'] =\
        test.find("#id_last_name").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['last_name']
    ##########  Changes to last name are saved to parse
    subscription.last_name = None
    parts[5]['success'] = subscription.get("last_name") ==\
        TEST_SUBSCRIPTION_INFO['last_name']
    ##########  Changes to card number are visible
    parts[6]['success'] =\
        test.find("#id_cc_number").get_attribute("value")[-4:] ==\
        TEST_SUBSCRIPTION_INFO['cc_number'][-4:]
    ##########  Changes to card number are saved to parse
    subscription.cc_number = None
    parts[7]['success'] = subscription.get("cc_number") ==\
        TEST_SUBSCRIPTION_INFO['cc_number'][-4:]
    ##########  A paypal credit card id is generated & saved
    # CARD-97223025G70599255KHHCCVQ
    subscription.pp_cc_id = None
    parts[8]['success'] = subscription.get("pp_cc_id").__contains__(\
        "CARD") and len(subscription.get("pp_cc_id")) == 29
    ##########  Changes to cc expiration are visible 
    parts[9]['success'] = month == test.get_selected("//select" +\
        "[@id='id_date_cc_expiration_month']/option",
        type="xpath").get_attribute("value") and\
        year == test.get_selected(\
        "//select[@id='id_date_cc_expiration_year']/option",
        type="xpath").get_attribute("value")
    ##########  Changes to cc expiration are saved to parse
    subscription.date_cc_expiration = None
    exp = subscription.get("date_cc_expiration")
    parts[10]['success'] = exp.month == TEST_SUBSCRIPTION_INFO[\
        'date_cc_expiration'].month and exp.year ==\
        TEST_SUBSCRIPTION_INFO['date_cc_expiration'].year
    ##########  Changes to address are visible
    parts[11]['success'] =\
        test.find("#id_address").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['address']
    ##########  Changes to address are saved to parse 
    subscription.address = None
    parts[12]['success'] = subscription.get("address") ==\
        TEST_SUBSCRIPTION_INFO['address']
    ##########  Changes to city are visible
    parts[13]['success'] =\
        test.find("#id_city").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['city']
    ##########  Changes to city are saved to parse 
    subscription.city = None
    parts[14]['success'] = subscription.get("city") ==\
        TEST_SUBSCRIPTION_INFO['city']
    ##########  Changes to state are visible
    parts[15]['success'] =\
        test.find("#id_state").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['state']
    ##########  Changes to state are saved to parse 
    subscription.state = None
    parts[16]['success'] = subscription.get("state") ==\
        TEST_SUBSCRIPTION_INFO['state']
    ##########  Changes to zip are visible
    parts[17]['success'] =\
        test.find("#id_zip").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['zip']
    ##########  Changes to zip are saved to parse 
    subscription.zip = None
    parts[18]['success'] = subscription.get("zip") ==\
        TEST_SUBSCRIPTION_INFO['zip']
    
    ## Make changes
    selectors = [
        "#id_first_name", "#id_last_name", 
        "#id_cc_number", "#id_cc_cvv",  
        "#id_address", "#id_city", "#id_state", "#id_zip",
    ]
    test.action_chain(0, selectors, action="clear")
    for i in range(len(selectors)):
        selectors[i] = (selectors[i], "    ")
    test.action_chain(0, selectors, action="send_keys")
    
    ##########  First name is required
    
    ##########  Last name is required TODO
    ##########  Card number is required TODO
    ##########  Security code (cvc) is required TODO
    ##########  Address is required TODO
    ##########  City is required TODO
    ##########  State is required TODO
    ##########  Zip is required TODO
    ##########  ToS checked is required TODO
    ##########  Invalid credit card number shows error TODO
    ##########  Past expiration date is invalid TODO
    ##########  Only the last 4 digits of the card number is shown TODO
    ##########  Not changing the card number does not TODO
    ######      generate new paypal credit card id
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()
    
    
    
