"""
Selenium tests for dashboard 'My Account' tab.
"""

from django.utils import timezone
from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoAlertPresentException
from dateutil.tz import tzutc
from datetime import datetime
from time import sleep
import math, requests

from tests import SeleniumTest
from parse.apps.accounts.models import Account

# TODO test passed_user_limit
# TODO test monthly_billing - failed to charge

IMAGE_UPLOAD = "/home/vestrel00/Pictures/wallpapers/test.png"

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

TEST_STORE_INFO = {
    "store_name": "Vandolf's Military Militia",
    "street": "952 Sutter St",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94109",
    "phone_number": "(111) 111-1111",
    "store_description": "Weapons so big they should be illegal.",
    "hours": [{"close_time":"0030","day":2,"open_time":"0000"},
            {"close_time":"0130","day":3,"open_time":"0100"},
            {"close_time":"0230","day":4,"open_time":"0200"},
            {"close_time":"0330","day":5,"open_time":"0300"},],
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

class TestEditStoreDetails(SeleniumTest):

    def __init__(self):
        super(TestEditStoreDetails, self).__init__(\
            user_include="Store.Subscription")
            
        self.store = self.account.store
        self.store.update_locally(STORE_INFO, False)
        self.store.update()
        
        ## Required fields are required!
        def fields_required():
            self.click_store_edit()
            sleep(3)
            selectors = (
                "#id_store_name", "#id_street", "#id_city",
                "#id_state", "#id_zip",
                "#Ph1", "#Ph2", "#Ph3",
            )
            self.action_chain(0, selectors, action="clear") 
            self.find("#save-button").click() 
            sleep(3)
            return True
        
        # tests 25 to 30
        self.fields_required((
            ("#store_name_e ul li", "Store name is required"),
            ("#street_e ul li", "Street is required"),
            ("#city_e ul li", "City is required"),
            ("#state_e ul li", "State is required"),
            ("#zip_e ul li", "Zip is required"),
            ("#phone_number_e ul li", "Phone number is required"),
        ), init_func=fields_required, test_offset=25)
        
    def click_store_edit(self):
        self.find("//div[@id='store-details']/a[@href='" +\
            reverse("store_edit") + "']", type="xpath").click() 
    
    def test_0(self):
        """
        User needs to be logged in to access page
        """
        self.open(reverse("store_index")) 
        sleep(1)
        return self.is_current_url(reverse(\
            'manage_login') + "?next=" + reverse("store_index"))
        
    def test_1(self):
        """
        Edit page reachable
        """
        # login
        selectors = (
            ("#login_username", self.USER['username']),
            ("#login_password", self.USER['password']),
            ("", Keys.RETURN)
        )
        self.action_chain(0, selectors, "send_keys") 
        sleep(7)
    
        self.click_store_edit() 
        sleep(3)
        return self.is_current_url(reverse("store_edit"))
     
    def test_2(self):
        """
        Changes to store name are visible 
        """   
        ### make all the changes
        selectors = (
            ("#id_store_name", TEST_STORE_INFO['store_name']),
            ("#id_street", TEST_STORE_INFO['street']),
            ("#id_city", TEST_STORE_INFO['city']),
            ("#id_state", TEST_STORE_INFO['state']),
            ("#id_zip", TEST_STORE_INFO['zip']),
            ("#Ph1", TEST_STORE_INFO['Ph1']),
            ("#Ph2", TEST_STORE_INFO['Ph2']),
            ("#Ph3", TEST_STORE_INFO['Ph3']),
            ("#id_store_description", TEST_STORE_INFO['store_description']),
        )
        self.action_chain(0, selectors, action="clear")
        self.action_chain(0, selectors, action="send_keys")
        
        # hours
        # [{"close_time":"0030","day":2,"open_time":"0000"},
        # {"close_time":"0130","day":3,"open_time":"0100"},
        # {"close_time":"0230","day":4,"open_time":"0200"},
        # {"close_time":"0330","day":5,"open_time":"0300"},]
        for i in range(4):
            istr = str(i)
                
            self.find("//ul[@id='hours-{0}-row']/".format(istr) +\
                "li[@class='days']/div[{0}]".format(str(i+2)),
                type="xpath").click()
            sleep(1)
            self.find("//ul[@id='hours-{0}-row']".format(istr)+\
                "/li[contains(@class, 'open')]/select[@name='hours-{0}-open']".format(istr) +\
                "/option[@value='0{0}00']".format(istr),
                type="xpath").click()
            sleep(1)
            self.find("//ul[@id='hours-{0}-row']".format(istr)+\
                "/li[contains(@class, 'close')]/select[@name='hours-{0}-close']".format(istr) +\
                "/option[@value='0{0}30']".format(istr),
                type="xpath").click()
            sleep(1)
            self.find(".hours-form div.add").click()
            
        # store the hours preview for comparison
        self.hours_prev = self.find("#store-hours-preview").text.split("\n")
        
        # save!
        self.find("#save-button").click()
        sleep(6)
        
        address = str(self.find("#address p").text).split("\n")
        l2 = address[1].split(", ")
        self.street = address[0]
        self.city = l2[0]
        self.state, self.zip = l2[1].split(" ")
        self.phone_number = address[2]
        
        self.store.fetch_all(clear_first=True, with_cache=True)

        return self.find("#address span").text ==\
            TEST_STORE_INFO['store_name']
    
    def test_3(self):
        """
        Changes to store name are saved to Parse 
        """
        return self.store.store_name == TEST_STORE_INFO['store_name']
        
    def test_4(self):
        """
        Changes to street are visible
        """
        return self.street == TEST_STORE_INFO['street']
    
    def test_5(self):
        """
        Changes to street are saved to Parse
        """
        return self.store.street == TEST_STORE_INFO['street']
            
    def test_6(self):
        """
        Changes to city are visible
        """
        return self.city == TEST_STORE_INFO['city']
    
    def test_7(self):
        """
        Changes to city are saved to Parse
        """
        return self.store.city == TEST_STORE_INFO['city']
    
    def test_8(self):
        """
        Changes to state are visible
        """
        return self.state == TEST_STORE_INFO['state']
    
    def test_9(self):
        """
        Changes to state are saved to Parse
        """
        return self.store.state == TEST_STORE_INFO['state']
    
    def test_10(self):
        """
        Changes to zip are visible
        """
        return self.zip == TEST_STORE_INFO['zip']
    
    def test_11(self):
        """
        Changes to zip are saved to Parse
        """
        return self.store.zip == TEST_STORE_INFO['zip']
    
    def test_12(self):
        """
        Changes to phone number are visible
        """
        return self.phone_number == TEST_STORE_INFO['phone_number']
    
    def test_13(self):
        """
        Changes to phone number are saved to Parse
        """
        return self.store.phone_number == TEST_STORE_INFO['phone_number']
    
    def test_14(self):
        """
        Changes to hours are visible
        """
        equal = True
        for hour in self.find("#hours").text.split("\n")[1:]:
            if hour not in self.hours_prev:
                equal = False
                break
                
        return equal
    
    def test_15(self):
        """
        Changes to hours are saved to Parse
        """
        equal = True
        for hour in self.store.hours:
            z = False
            for x in TEST_STORE_INFO['hours']:
                if hour["day"] == x["day"] and hour["open_time"] ==\
                    x["open_time"] and hour["close_time"] ==\
                    x["close_time"]:
                    z = True
                    break
            if not z:
                equal = False
                break

        return equal
    
    def test_16(self):
        """
        Changing the zip changes the store_timezone
        """
        return self.store.store_timezone == TEST_STORE_INFO['store_timezone']
    
    def test_17(self):
        """
        Changing the zip changes the neighborhood 
        """
        return self.store.neighborhood == TEST_STORE_INFO['neighborhood']
    
    def test_18(self):
        """
        Changing the zip changes the coordinates 
        """
        return int(math.floor(self.store.coordinates[0])) ==\
            int(math.floor(TEST_STORE_INFO['coordinates'][0])) and\
            int(math.floor(self.store.coordinates[1])) ==\
            int(math.floor(TEST_STORE_INFO['coordinates'][1]))
    
    def test_19(self):
        """
        Entering invalid address shows error
        """
        self.click_store_edit()
        sleep(3)
        selectors = (
            ("#id_street", "988 dsgsd s"),
            ("#id_city", "mandarin"),
            ("#id_state", "klk"),
            ("#id_zip", "941091"),
        )        
        self.action_chain(0, selectors, action="clear")
        self.action_chain(0, selectors, action="send_keys")
        
        # save!
        self.find("#save-button").click()
        sleep(3)
        
        return self.find(".errorlist").text ==\
            "Enter a valid adress, city, state, and/or zip."
            
    def test_20(self):
        """        
        Entering invalid hours with same open time as close time shows error
        """
        self.find("//div[@id='edit-store-options']/a[2]",
            type="xpath").click()
        sleep(2)
        
        self.click_store_edit()
        sleep(3)
        
        self.find("//ul[@id='hours-0-row']"+\
            "/li[contains(@class, 'open')]/select[@name='hours-0-open']" +\
            "/option[@value='0000']", type="xpath").click()
        sleep(1)
        self.find("//ul[@id='hours-0-row']"+\
            "/li[contains(@class, 'close')]/select[@name='hours-0-close']" +\
            "/option[@value='0000']", type="xpath").click()
            
        return self.find("#hours_e > .errorlist > li").text ==\
            "The opening time cannot be the same as the closing time."
        
    def test_21(self):
        """
        Entering invalid hours with later open time than close time shows error
        """
        self.find("//ul[@id='hours-0-row']"+\
            "/li[contains(@class, 'open')]/select[@name='hours-0-open']" +\
            "/option[@value='0030']", type="xpath").click()
        sleep(1)
        self.find("//ul[@id='hours-0-row']"+\
            "/li[contains(@class, 'close')]/select[@name='hours-0-close']" +\
            "/option[@value='0000']", type="xpath").click()
            
        return self.find("#hours_e > .errorlist > li").text ==\
            "The opening time cannot be later than the closing time."
    
    def test_22(self):
        """
        Having no hours is allowed
        """
        for i in range(4):
            self.find("//ul[@id='hours-{0}-row']".format(str(i))+\
                "/li[@class='buttons']/div[@class='remove']",
                type="xpath").click()
            
        self.find("#save-button").click()
        sleep(6)
        self.store.hours = None
        return self.find("#hours").text.split("\n")[1] ==\
            'Closed Sunday - Saturday' and\
            len(self.store.get("hours")) == 0
        
    def test_23(self):
        """
        24/7 Hours is functional
        """
        self.click_store_edit()
        sleep(3)
        self.find("#open-24-7-label").click()
        sleep(2)
        return self.find("#slide-container").value_of_css_property(\
            "display") == "none" and\
            self.find("#store-hours-preview").text == "Open 24/7"
        
    def test_24(self):
        """
        24/7 Hours is saved as [{"day":0}]
        """
        self.find("#save-button").click()
        sleep(6)
        self.store.hours = None
        return self.store.get("hours")[0]["day"] == 0
    
    def test_31(self):
        """
        Cancel button redirects user back to store index
        """
        self.find("//div[@id='edit-store-options']/a[2]",
            type="xpath").click()
        sleep(2)
        return self.is_current_url(reverse('store_index'))
    
    def test_32(self):
        """
        Clicking Add/Change Photo brings up the image upload dialog/frame
        """
        self.click_store_edit()
        sleep(3)
        self.find("#upload-avatar").click()
        sleep(1)
        self.driver.switch_to_frame(self.find("iframe", type='tag_name'))
        
        return self.find("#edit-avatar-options").is_displayed()
    
    def test_33(self):
        """
        Clicking cancel on upload removes the dialog /frame
        """
        self.find("//div[@id='edit-avatar-options']/a[2]",
            type="xpath").click()
        sleep(1)
        return self.element_exists("#edit-store-options")
        
    def test_34(self):
        """
        Clicking upload when no file is selected shows alert
        """
        self.find("#upload-avatar").click()
        sleep(1)
        # switch to frame!
        self.driver.switch_to_frame(\
            self.find("iframe", type='tag_name'))
        self.find("#upload-btn").click()
        sleep(1)
        alert = self.switch_to_alert()
        success = str(alert.text) ==\
            "Please select an image to upload."
        alert.accept()
        return success
    
    def test_35(self):
        """
        Uploading images works
        """
        self.find("#id_image").send_keys(IMAGE_UPLOAD)
        self.find("#upload-btn").click()
        sleep(3)
        return self.find("#crop-btn").is_displayed()
    
    def test_36(self):
        """
        Clicking cancel on crop removes the dialog
        """
        self.find("//div[@id='edit-avatar-options']/a[2]",
            type="xpath").click()
        sleep(1)
        return self.element_exists("#edit-store-options")
        
    def test_37(self):
        """
        Cropping images works
        """
        self.find("#upload-avatar").click()
        sleep(1)
        self.driver.switch_to_frame(\
            self.find("iframe", type='tag_name'))
        self.find("#id_image").send_keys(IMAGE_UPLOAD)
        self.find("#upload-btn").click()
        sleep(3)
        self.find("#crop-btn").click()
        return True
    
    def test_38(self):
        """
        New store avatar is saved to Parse
        """
        sleep(5)
        self.old_avatar_url = self.store.store_avatar_url
        self.store.store_avatar = None
        self.store.store_avatar_url = None
        self.new_avatar_url = self.store.get("store_avatar_url")
        
        return self.old_avatar_url != self.new_avatar_url
    
    def test_39(self):
        """
        Old store avatar is deleted from Parse files
        """
        resp = requests.get(self.old_avatar_url)
        return not resp.ok and resp.status_code == 403
    
    def test_40(self):
        """
        The store avatar thumbnail and image in store details/edit
        match the one saved in Parse
        """
        return self.new_avatar_url ==\
            self.find("#store_avatar").get_attribute("src") and\
            self.new_avatar_url ==\
            self.find("#avatar-thumbnail").get_attribute("src")
    
    
def test_update_subscription():
    # TODO test place_order
    account =  Account.objects().get(username=TEST_USER['username'],
        include="Store.Subscription")
    store = account.store
    subscription = store.subscription
    subscription.update_locally(SUBSCRIPTION_INFO, False)
    subscription.update()
    
    
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
            " are shown"},
        {'test_name': "Not changing the card number does not " +\
            "generate new paypal credit card id"},
    ]
    section = {
        "section_name": "Edit account/subscription working properly?",
        "parts": parts,
    }
    self.results.append(section)
    
    ##########  User needs to be logged in to access page
    self.open(reverse("store_index")) 
    sleep(1)
    parts[0]['success'] = self.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("store_index"))
        
    # login
    selectors = (
        ("#login_username", TEST_USER['username']),
        ("#login_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    self.action_chain(0, selectors, "send_keys") 
    sleep(7)  
   
    ##########  Update account page reachable
    try:
        self.find("//div[@id='account-options']/a[1]",
            type="xpath").click()
        sleep(3)
        parts[1]['success'] =\
            self.is_current_url(reverse("subscription_update"))
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
    
    ## Make changes
    # first clear all inputs
    for el in self.find("input[type='text']", multiple=True):
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
    self.action_chain(0, selectors, action="send_keys")
    month_el =\
        self.find("//select[@id='id_date_cc_expiration_month']/" +\
            "option[@value='%s']" % (str(TEST_SUBSCRIPTION_INFO[\
                'date_cc_expiration'].month),), type="xpath")
    year_el =\
        self.find("//select[@id='id_date_cc_expiration_year']/" +\
            "option[@value='%s']" % (str(TEST_SUBSCRIPTION_INFO[\
                'date_cc_expiration'].year),), type="xpath")
    month = month_el.get_attribute("value")
    year = year_el.get_attribute("value")
    month_el.click()
    year_el.click()
    
    self.find("#id_recurring").click()
    self.find("#update-form-submit").click()
    sleep(5)
    
    # back to update account page
    self.find("//div[@id='account-options']/a[1]",
        type="xpath").click()
    sleep(3)
    
    ##########  Changes to first name are visible
    parts[2]['success'] =\
        self.find("#id_first_name").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['first_name']
    ##########  Changes to first name are saved to parse
    subscription.first_name = None
    parts[3]['success'] = subscription.get("first_name") ==\
        TEST_SUBSCRIPTION_INFO['first_name']
    ##########  Changes to last name are visible
    parts[4]['success'] =\
        self.find("#id_last_name").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['last_name']
    ##########  Changes to last name are saved to parse
    subscription.last_name = None
    parts[5]['success'] = subscription.get("last_name") ==\
        TEST_SUBSCRIPTION_INFO['last_name']
    ##########  Changes to card number are visible
    parts[6]['success'] =\
        self.find("#id_cc_number").get_attribute("value")[-4:] ==\
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
    parts[9]['success'] = month == self.get_selected("//select" +\
        "[@id='id_date_cc_expiration_month']/option",
        type="xpath").get_attribute("value") and\
        year == self.get_selected(\
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
        self.find("#id_address").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['address']
    ##########  Changes to address are saved to parse 
    subscription.address = None
    parts[12]['success'] = subscription.get("address") ==\
        TEST_SUBSCRIPTION_INFO['address']
    ##########  Changes to city are visible
    parts[13]['success'] =\
        self.find("#id_city").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['city']
    ##########  Changes to city are saved to parse 
    subscription.city = None
    parts[14]['success'] = subscription.get("city") ==\
        TEST_SUBSCRIPTION_INFO['city']
    ##########  Changes to state are visible
    self.find("//select[@id='id_date_cc_expiration_year']/" +\
            "option[@value='%s']" % (str(TEST_SUBSCRIPTION_INFO[\
                'date_cc_expiration'].year)), type="xpath")
    parts[15]['success'] =\
        self.find("#id_state").get_attribute("value") ==\
        TEST_SUBSCRIPTION_INFO['state']
    ##########  Changes to state are saved to parse 
    subscription.state = None
    parts[16]['success'] = subscription.get("state") ==\
        TEST_SUBSCRIPTION_INFO['state']
    ##########  Changes to zip are visible
    parts[17]['success'] =\
        self.find("#id_zip").get_attribute("value") ==\
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
    self.action_chain(0, selectors, action="clear")
    for i in range(len(selectors)):
        selectors[i] = (selectors[i], "    ")
    self.action_chain(0, selectors, action="send_keys")
    
    self.find("#update-form-submit").click()
    sleep(3)
    
    ##########  First name is required
    ##########  Last name is required
    ##########  Card number is required
    ##########  Security code (cvc) is required 
    ##########  Address is required 
    ##########  City is required 
    ##########  State is required 
    ##########  Zip is required 
    ##########  ToS checked is required 
    def field_is_required(part, selector,
        message="This field is required."):
        try:
            parts[part]['success'] = self.find(selector).text==message
        except Exception as e:
            print e
            parts[part]['test_message'] = str(e)
    
    selectors = (
        (19, "#first_name_ic ul.errorlist li"),
        (20, "#last_name_ic ul.errorlist li"),
        (21, "#card_number_container ul.errorlist li",
            "Enter a valid credit card number."),
        (22, "#cc_cvv_ic ul.errorlist li"),
        (23, "#address_ic ul.errorlist li"),
        (24, "#city_ic ul.errorlist li"),
        (25, "#state_ic ul.errorlist li"),
        (26, "#zip_ic ul.errorlist li"),
        (27, "#recurring_charge_container ul.errorlist li",
            "You must accept the Terms & Conditions to continue."),
    )
    
    for selector in selectors:
        field_is_required(*selector)
    
    ##########  Invalid credit card number shows error
    try:
        cc_number = self.find("#id_cc_number")
        cc_number.clear()
        cc_number.send_keys("8769233313929990")
        self.find("#update-form-submit").click()
        sleep(3)
        parts[28]['success'] = self.find("#card_number_container " +\
            "ul.errorlist li").text ==\
                "Enter a valid credit card number."
    except Exception as e:
        print e
        parts[28]['test_message'] = str(e)
    
    ##########  Past expiration date is invalid
    if timezone.now().month == 1:
        # note that if this test is being run on a January, this will 
        # fail so to prevent that just skip the test if it is January
        parts[29]['test_message'] = "READ ME. This test has been " +\
            "skipped because the month is January, which means " +\
            "that this test will always fail due to limited " +\
            "select options."
    else:
        try:
            # select january of this year.
            self.find("//select[@id='id_date_cc_expiration_month']/" +\
                    "option[@value='1']", type="xpath").click()
            self.find("//select[@id='id_date_cc_expiration_year']/" +\
                    "option[@value='%s']" %\
                    (str(timezone.now().year),), type="xpath").click()
            self.find("#update-form-submit").click()
            sleep(3)
            parts[29]['success'] =\
                self.find("#date_cc_expiration_ic ul.errorlist " +\
                "li").text == "Your credit card has expired!"
        except Exception as e:
            print e
            parts[29]['test_message'] = str(e)
        
    ##########  Only the last 4 digits of the card number are shown
    try:
        self.find("//div[@class='form-options']/a[2]",
            type="xpath").click()
        sleep(1)
        self.find("//div[@id='account-options']/a[1]",
            type="xpath").click()
        sleep(3)
        masked_number =\
            self.find("#id_cc_number").get_attribute("value")
        parts[30]['success'] = masked_number[:-4] ==\
            "************" and str(masked_number[-4:]).isdigit()
    except Exception as e:
        print e
        parts[30]['test_message'] = str(e)
    
    ##########  Not changing the card number does not
    ######      generate new paypal credit card id
    try:
        subscription.pp_cc_id = None
        cc_id = subscription.get("pp_cc_id")
        self.find("#id_cc_cvv").send_keys("123")
        self.find("#id_recurring").click()
        self.find("#update-form-submit").click()
        sleep(5)
        subscription.pp_cc_id = None
        parts[31]['success'] = cc_id == subscription.get("pp_cc_id")
    except Exception as e:
        print e
        parts[31]['test_message'] = str(e)
    
    # END OF ALL TESTS - cleanup
    return self.tear_down()
    
def test_cancel_account():
    """
    A test just for the cancel account link.
    """
    account =  Account.objects().get(username=TEST_USER['username'],
        include="Store")
    store = account.store
    
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Clicking the cancel button brings up a " +\
            "confirmation dialog"},
        {'test_name': "Clicking cancel on the dialog dimisses the " +\
            "dialog and the account remains active"},
        {'test_name': "Clicking OK logs the user out"},
        {'test_name': "Clicking OK sets the store's active field " +\
            "to false on Parse"},
    ]
    section = {
        "section_name": "Deactivate store link functional?",
        "parts": parts,
    }
    self.results.append(section)
    
    ##########  User needs to be logged in to access page
    self.open(reverse("store_index")) 
    sleep(1)
    parts[0]['success'] = self.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("store_index"))
        
    # login
    selectors = (
        ("#login_username", TEST_USER['username']),
        ("#login_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    self.action_chain(0, selectors, "send_keys") 
    sleep(7)  
    
    ##########  Clicking the cancel button brings up a confrmtn dialog
    try:
        self.find("#deactivate_account").click()
        sleep(1)
        alert = self.switch_to_alert()
        parts[1]['success'] = alert is not None
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
        
    ##########  Clicking cancel on the dialog dimisses the 
    ###         dialog and the account remains active
    try:
        alert.dismiss()
        try:
            alert.text
        except NoAlertPresentException:
            store.active = None
            parts[2]['success'] = store.get("active")
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
        
    ##########  Clicking OK logs the user out
    try:
        self.find("#deactivate_account").click()
        sleep(1)
        alert = self.switch_to_alert()
        alert.accept()
        sleep(4)
        if SeleniumTest.DEV_LOGIN:
            parts[3]["success"] =\
                self.is_current_url(reverse("manage_dev_login")+"?next=/")
        else:
            parts[3]["success"] =\
                self.is_current_url(reverse("public_home"))
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
        
    ##########  Clicking OK sets the store's active 
    ###         field to false on Parse
    store.active = None
    parts[4]['success'] = not store.get("active")
    
    # undo
    store.active = True
    store.update()
    
    # END OF ALL TESTS - cleanup
    return self.tear_down()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
