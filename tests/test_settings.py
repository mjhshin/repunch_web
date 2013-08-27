"""
Selenium tests for dashboard 'Settings' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest
from parse.apps.accounts.models import Account

TEST_USER = {
    "username": "clothing@vandolf.com",
    "password": "123456",
}


def test_settings():
    # setup
    account = Account.objects().get(username=TEST_USER['username'],
        include="Store.Settings")
    store = account.store
    settings = store.settings
    
    # set punches facebook and employees to 1
    store.punches_facebook = 1
    settings.punches_employee = 1
    store.update()
    settings.update()
    
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Changes to Punches employee are visible"},
        {'test_name': "Changes to Punches facebook are visible"},
        {'test_name': "Changes to Punches employee are saved to Parse"},
        {'test_name': "Changes to Punches facebook are saved to Parse"},
        {'test_name': "Punches employee is required"},
        {'test_name': "Punches facebook is required"},
        {'test_name': "Punches employee must be a number"},
        {'test_name': "Punches facebook must be a number."},
        {'test_name': "Punches employee must be greater than 0"},
        {'test_name': "Punches facebook must be greater than or = 0"},
        {'test_name': "Retailer PIN is refreshable"},
        {'test_name': "Changes to Retailer PIN is immediately " +\
            "commited to Parse without having to save settings."},
        {'test_name': "Clicking cancle redirects user back to " +\
            "settings page"},
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
        'manage_login') + "?next=" + reverse("account_settings"))
        
    # login
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(5) 
    
    try:
        selectors = (
            ("#id_punches_employee", "5"),
            ("#id_punches_facebook", "5"),
        )
        test.action_chain(0, selectors, action="clear")
        test.action_chain(0, selectors, action="send_keys")
        test.find("#settings-form-submit").click()
        sleep(5)
    except Exception as e:
        print e
        
    ##########  Changes to Punches employee are visible
    try:
        parts[1]['success'] = test.find(\
            "#id_punches_employee").get_attribute("value") == "5"
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
        
    ##########  Changes to Punches facebook are visible
    try:
        parts[2]['success'] = test.find(\
            "#id_punches_facebook").get_attribute("value") == "5"
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
    ##########  Changes to Punches employee are saved to Parse
    try:
        settings.punches_employee = None
        parts[3]['success'] = settings.get("punches_employee") ==\
            int(test.find("#id_punches_employee").get_attribute("value"))
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
    ##########  Changes to Punches facebook are saved to Parse
    try:
        store.punches_facebook = None
        parts[4]['success'] = store.get("punches_facebook") ==\
            int(test.find("#id_punches_facebook").get_attribute("value"))
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
    
    try:
        selectors = ("#id_punches_employee", "#id_punches_facebook")
        test.action_chain(0, selectors, action="clear")
        test.find("#settings-form-submit").click()
        sleep(1)
    except Exception:
        pass
    
    ##########  Punches employee is required
    try:
        parts[5]['success'] =\
            test.find("#punches_employee_e ul li").text ==\
                "This field is required."
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
    ##########  Punches facebook is required
    try:
        parts[6]['success'] =\
            test.find("#punches_facebook_e ul li").text ==\
                "This field is required."
    except Exception as e:
        print e
        parts[6]['test_mesage'] = str(e)
    
    try:  
        selectors = (
            ("#id_punches_employee", "a"), 
            ("#id_punches_facebook", "b"), 
        )
        test.action_chain(0, selectors, action="clear")
        test.action_chain(0, selectors, action="send_keys")
        test.find("#settings-form-submit").click()
        sleep(1)
    except Exception:
        pass
    
    ##########  Punches employee must be a number
    try:
        parts[7]['success'] =\
            test.find("#punches_employee_e ul li").text==\
            "Enter a whole number."
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
    ##########  Punches facebook must be a number 
    try:   
        parts[8]['success'] =\
            test.find("#punches_facebook_e ul li").text==\
            "Enter a whole number."
    except Exception as e:
        print e
        parts[8]['test_message'] = str(e)
        
    try:  
        selectors = (
            ("#id_punches_employee", "-1"), 
            ("#id_punches_facebook", "-1"), 
        )
        test.action_chain(0, selectors, action="clear")
        test.action_chain(0, selectors, action="send_keys")
        test.find("#settings-form-submit").click()
        sleep(1)
    except Exception:
        pass
    ##########  Punches employee must be greater than 0
    try:   
        parts[9]['success'] =\
            test.find("#punches_employee_e ul li").text ==\
            "Ensure this value is greater than or equal to 1."
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
    ##########  Punches facebook must be greater than or equal to 0
    try:   
        parts[10]['success'] =\
            test.find("#punches_facebook_e ul li").text ==\
            "Ensure this value is greater than or equal to 0."
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
    ##########  Retailer PIN is refreshable
    try:
        prev_pin = test.find("#retailer_pin").text
        test.find("#link_refresh_retailer_pin").click()
        sleep(10) # yea this takes a while
        new_pin = test.find("#retailer_pin").text
        parts[11]['success'] = prev_pin != new_pin
    except Exception as e:
        print e
        parts[11]['test_message'] = str(e)
    ##########  Changes to Retailer PIN is immediately
    ###         commited to Parse without having to save settings
    try:
        settings.retailer_pin = None
        parts[12]['success'] = settings.get("retailer_pin") == new_pin
    except Exception as e:
        print e
        parts[12]['test_message'] = str(e)
    
    ##########  Clicking cancel redirects user back to settings page
    try:
        current_pin = test.find("#retailer_pin").text
        test.find("//div[@id='settings-options']/a[2]",
            type="xpath").click()
        sleep(1)
        parts[13]['success'] =\
            test.is_current_url(reverse("account_settings"))
    except Exception as e:
        print e
        parts[13]['test_message'] = str(e)
    
    ##########  Clicking cancel changes will not undo the 
    ###         change made to Retailer PIN
    try:
        parts[14]['success'] = current_pin ==\
            test.find("#retailer_pin").text
    except Exception as e:
        print e
        parts[14]['test_message'] = str(e)
        
    ##########  Clicking cancel changes will not save 
    ###         changes to punches facebook and punches employee
    try:
        current_ep =\
            test.find("#id_punches_employee").get_attribute("value")
        current_fbp =\
            test.find("#id_punches_facebook").get_attribute("value")
        test.find("//div[@id='settings-options']/a[2]",
            type="xpath").click()
        sleep(1)
        parts[15]['success'] = current_ep == test.find(\
            "#id_punches_employee").get_attribute("value") and\
            current_fbp == test.find(\
            "#id_punches_facebook").get_attribute("value")
    except Exception as e:
        print e
        parts[15]['test_message'] = str(e)
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
