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
    # TODO test employee graph
    
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
        {'test_name': "Clicking deny prompts the user to confirm"},
        {'test_name': "The user is redirected to employee index"},
        {'test_name': "The denied employee is removed from the " +\
            "pending table"},
        {'test_name': "The employee is deleted from parse"},
        {'test_name': "The account/user is deleted from parse"},
        {'test_name': "Approving the employee moves it from " +\
            "pending to approved"},
        {'test_name': "Employee status is set to approved in Parse"},
        {'test_name': "Employee initially has 0 punches."},
        {'test_name': "Clicking on the approved employee row " +\
            " redirects user to employee edit page"},
        {'test_name': "Clicking delete prompts the user to confirm"},
        {'test_name': "The user is redirected to employee index"},
        {'test_name': "The denied employee is removed from the " +\
            "pending table"},
        {'test_name': "The employee is deleted from parse"},
        {'test_name': "The account/user is deleted from parse"},
        {'test_name': "Multiple employees (4) registering at once" +\
            " works"},
        {'test_name': "Approving 2 employees in succession works"},
        {'test_name': "Removing 2 employees in succession works"},
        {'test_name': "Denying 2 employees in succession works"},
    ]
    section = {
        "section_name": "Employees page punching working properly?",
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
    
    def register_employee(first_name, last_name, username=None, 
        password=None, email=None, retailer_pin=None):
        
        if username is None: 
            username = first_name
        if password is None: 
            password = first_name
        if email is None: 
            email = first_name + "@" + last_name + ".com"
        if retailer_pin is None: 
            retailer_pin = settings.retailer_pin
            
        return cloud_call("register_employee", {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "password": password,
            "email": email,
            "retailer_pin": retailer_pin,
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
    ##########  Email must be valid (cloud code) TODO
    try:
        pass
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
    ##########  Email must be unique (cloud code) TODO
    try:
        pass
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
    ##########  Username must be unique (cloud code) TODO
    try:
        pass
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
    ##########  Retailer PIN must exist (cloud code) TODO
    try:
        pass
    except Exception as e:
        print e
        parts[8]['test_message'] = str(e)
    ##########  Clicking deny prompts the user to confirm TODO
    try:
        pass
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
    ##########  The user is redirected to employee index TODO
    try:
        pass
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
    ##########  The denied employee is removed from the pending table TODO
    try:
        pass
    except Exception as e:
        print e
        parts[11]['test_message'] = str(e)
    ##########  The employee is deleted from parse TODO
    try:
        pass
    except Exception as e:
        print e
        parts[12]['test_message'] = str(e)
    ##########  The account/user is deleted from parse TODO
    try:
        pass
    except Exception as e:
        print e
        parts[13]['test_message'] = str(e)
    ##########  Approving the employee moves it from 
    ###         pending to approved TODO
    try:
        pass
    except Exception as e:
        print e
        parts[14]['test_message'] = str(e)
    ##########  Employee status is set to approved in Parse TODO
    try:
        pass
    except Exception as e:
        print e
        parts[15]['test_message'] = str(e)
    ##########  Employee initially has 0 punches TODO
    try:
        pass
    except Exception as e:
        print e
        parts[16]['test_message'] = str(e)
    ##########  Clicking on the approved employee row 
    ###         redirects user to employee edit page  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[17]['test_message'] = str(e)
    ##########  Clicking delete prompts the user to confirm TODO
    try:
        pass
    except Exception as e:
        print e
        parts[18]['test_message'] = str(e)
    ##########  The user is redirected to employee index TODO
    try:
        pass
    except Exception as e:
        print e
        parts[19]['test_message'] = str(e)
    ##########  The denied employee is removed from the pending table TODO
    try:
        pass
    except Exception as e:
        print e
        parts[20]['test_message'] = str(e)
    ##########  The employee is deleted from parse TODO
    try:
        pass
    except Exception as e:
        print e
        parts[21]['test_message'] = str(e)
    ##########  The account/user is deleted from parse TODO
    try:
        pass
    except Exception as e:
        print e
        parts[22]['test_message'] = str(e)
    ##########  Multiple employees (4) registering at once works TODO
    try:
        pass
    except Exception as e:
        print e
        parts[23]['test_message'] = str(e)
    ##########  Approving 2 employees in succession works TODO
    try:
        pass
    except Exception as e:
        print e
        parts[24]['test_message'] = str(e)
    ##########  Removing 2 employees in succession works TODO
    try:
        pass
    except Exception as e:
        print e
        parts[25]['test_message'] = str(e)
    ##########  Denying 2 employees in succession works TODO
    try:
        pass
    except Exception as e:
        print e
        parts[26]['test_message'] = str(e)
    
    
    
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
