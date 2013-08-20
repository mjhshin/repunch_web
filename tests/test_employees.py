"""
Selenium tests for dashboard 'Employees' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest
from parse.utils import cloud_call
from parse.apps.accounts.models import Account
from parse.apps.employees import PENDING
from repunch.settings import COMET_PULL_RATE

TEST_USER = {
    "username": "clothing",
    "password": "123456",
}

def test_employees():
    """
    Tests for employee approve, deny, remove, details. etc.
    """
    # clear the employees relation
    account = Account.objects().get(username=TEST_USER['username'],
        include="Store.Settings")
    store = account.store
    settings = store.settings
    
    emps = store.get("employees")
    if emps:
        store.remove_relation("Employees_",
            [emp.objectId for emp in emps])
    
    store.set("employees", None)  
    
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Cloud code register_employee works"},
        {'test_name': "Employee is saved in store's Employees " +\
            "relation"},
        {'test_name': "Employee is initially pending (Parse)"},
        {'test_name': "Employee is initially pending (Dashboard)"},
        {'test_name': "Email must be valid (cloud code)"},
        {'test_name': "Email must be unique (cloud code)"},
        {'test_name': "Username must be unique (cloud code)"},
        {'test_name': "Retailer PIN must exist (cloud code)"},
    ]
    section = {
        "section_name": "Workbench page punching working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("employees_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("employees_index"))
        
    # login
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(5) 
    
    def register_employee(first, last):
        return cloud_call("register_employee", {
            "first_name": first,
            "last_name": last,
            "username":first,
            "password":first,
            "email":first + "@" + "qwerty.com",
            "retailer_pin": settings.retailer_pin,
        })
        
    ##########  Cloud code register_employee works
    try:
        res = register_employee("vandolf1", "estrellado1")
        parts[1]['success'] = res.get("result") == "success"
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
    ########## Employee is saved in store's Employees relation
    try:
        emp = store.get("employees")[0]
        parts[2]['success'] = emp is not None
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
    ##########  Employee is initially pending (Parse)
    try:
        parts[3]['success'] = emp.status == PENDING
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
    ##########  Employee is initially pending (Dashboard)
    try:
        sleep(COMET_PULL_RATE*2 + 1) # wait for dashboard to receive
        test.find("#tab-pending-employees").click()
        parts[4]['success'] = test.element_exists(\
            "#tab-body-pending-employees ")
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
