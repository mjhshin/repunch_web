"""
Selenium tests for dashboard 'Employees' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from urllib import urlencode
import re

from tests import SeleniumTest
from parse.test import register_employee, register_rand_employee,\
request_redeem_ps
from parse.utils import cloud_call
from parse.apps.accounts.models import Account
from parse.apps.employees import PENDING, APPROVED
from repunch.settings import COMET_PULL_RATE
from parse.apps.stores import ACCESS_ADMIN, ACCESS_PUNCHREDEEM,\
ACCESS_NONE

TEST_USER = {
    "username": "violette87@repunch.com",
    "password": "repunch7575",
}

def test_employees():
    """
    Tests for employee approve, deny, remove, details. etc.
    """
    # TODO test employee graph
    # TODO test employee punches history
    
    # delete the employees and associated User objects in the relation
    account = Account.objects().get(username=TEST_USER['username'],
        include="Store.Settings")
    store = account.store
    settings = store.settings
    
    emps = store.get("employees")
    if emps:
        for emp in emps:
            Account.objects().get(Employee=emp.objectId).delete()
            emp.delete()
    
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
        {'test_name': "The deleted employee is removed from the " +\
            "pending table"},
        {'test_name': "The employee is deleted from parse"},
        {'test_name': "The account/user is deleted from parse"},
        {'test_name': "Multiple employees (3) registering at once" +\
            " shows up in dashboard"},
    ]
    section = {
        "section_name": "Employees page working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page"
    test.open(reverse("employees_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("employees_index"))
        
    # login
    selectors = (
        ("#login_username", TEST_USER['username']),
        ("#login_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(7) 
    
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
        
    first_name, last_name, username, email =\
    "vandolf1", "estrellado", "xmanvman@xman.com", "xmanvman@xman.com"
        
    ##########  Cloud code register_employee works"
    try:
        res = register_employee(first_name, last_name, username,
            email=email)
        parts[1]['success'] = "error" not in res
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
    ##########  Employee is saved in store's Employees relation"
    try:
        emp = store.get("employees")[0]
        parts[2]['success'] = emp is not None
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
    ##########  Employee is initially pending (Parse)"
    try:
        parts[3]['success'] = emp.status == PENDING
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
    ##########  Employee is initially pending (Dashboard)"
    try:
        sleep(COMET_PULL_RATE*2 + 1) # wait for dashboard to receive
        test.find("#tab-pending-employees").click()
        parts[4]['success'] = test.element_exists(\
            "#tab-body-pending-employees div.tr div.td.approve")
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
    ##########  Email must be valid (cloud code)"
    try:
        res = register_employee("vman", "vman", email="vmahs@vman")
        parts[5]['success'] = res['error'] == 'EMAIL_INVALID'
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
    ##########  Email must be unique (cloud code) "
    try:
        res = register_employee("vman", "vman",
            email=email)
        parts[6]['success'] = res['error'] == 'EMAIL_TAKEN'
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
    ##########  Username must be unique (cloud code) "
    try:
        res = register_employee("vman", "vman", username=username)
        parts[7]['success'] = res['error'] == 'USERNAME_TAKEN'
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
    ##########  Retailer PIN must exist (cloud code) "
    try:
        res = register_employee("vman", "vman", retailer_pin="sdgdgs")
        parts[8]['success'] = res['error'] == "RETAILER_PIN_INVALID"
    except Exception as e:
        print e
        parts[8]['test_message'] = str(e)
    ##########  Clicking deny prompts the user to confirm"
    try:
        test.find("#tab-pending-employees").click()
        test.find("#tab-body-pending-employees div.tr " +\
            "div.td.approve a.deny").click()
        alert = test.switch_to_alert()
        parts[9]['success'] = alert.text == "Deny employee?"
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
    ##########  The user is redirected to employee index"
    try:
        sleep(1)
        alert.accept()
        sleep(2)
        parts[10]['success'] = test.is_current_url(reverse(\
            "employees_index") +\
            "?show_pending&success=Employee+has+been+denied.")
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
    ##########  The denied employee is removed from the pending table"
    try:
        parts[11]['success'] = not test.element_exists(\
        "#tab-body-pending-employees div.tr " +\
            "div.td.approve a.approve")
    except Exception as e:
        print e
        parts[11]['test_message'] = str(e)
    ##########  The employee is deleted from parse"
    try:
        store.set("employees", None)
        parts[12]['success'] = store.get("employees",\
            first_name=first_name, last_name=last_name, count=1) == 0
    except Exception as e:
        print e
        parts[12]['test_message'] = str(e)
    ##########  The account/user is deleted from parse"
    try:
        parts[13]['success'] = Account.objects().count(\
            username=username, email=email) == 0
    except Exception as e:
        print e
        parts[13]['test_message'] = str(e)
    ##########  Approving the employee moves it from pending to approved"
    try:
        register_employee(first_name, last_name, username,
            email=email)
        sleep(COMET_PULL_RATE*2 + 1) # wait for dashboard to receive
        test.find("#tab-pending-employees").click()
        approveRow = test.find("#tab-body-pending-employees " +\
            "div.tr")
        approveId = approveRow.get_attribute("id")
        approveRow.find_element_by_css_selector(\
            "div.td.approve a.approve").click()
        sleep(1)
        test.switch_to_alert().accept()
        sleep(2)
        test.find("#tab-approved-employees").click()
        parts[14]['success'] = test.element_exists(\
            "#tab-body-approved-employees " +\
            "div.tr div.td.remove a")
    except Exception as e:
        print e
        parts[14]['test_message'] = str(e)
    ##########  Employee status is set to approved in Parse"
    try:
        store.set("employees", None)
        emp = store.get("employees", first_name=first_name,
            last_name=last_name)[0]
        parts[15]['success'] = emp.status == APPROVED
    except Exception as e:
        print e
        parts[15]['test_message'] = str(e)
    ##########  Employee initially has 0 punches"
    try:
        parts[16]['success'] = emp.lifetime_punches == 0
    except Exception as e:
        print e
        parts[16]['test_message'] = str(e)
    ##########  Clicking on the approved employee row 
    ###         redirects user to employee edit page 
    try:
        test.find("#tab-approved-employees").click()
        test.find("#tab-body-approved-employees div#%s a" %\
            (emp.objectId,)).click()
        sleep(1)
        parts[17]['success'] = test.is_current_url(reverse(\
            "employee_edit", args=(emp.objectId,)))
    except Exception as e:
        print e
        parts[17]['test_message'] = str(e)
    ##########  Clicking delete prompts the user to confirm"
    try:
        test.find("#delete-button").click()
        alert = test.switch_to_alert()
        parts[18]['success'] = alert.text ==\
            "Are you sure you want to delete this employee?"
    except Exception as e:
        print e
        parts[18]['test_message'] = str(e)
    ##########  The user is redirected to employee index"
    try:
        sleep(1)
        alert.accept()
        sleep(2)
        parts[19]['success'] = test.is_current_url(reverse(\
            "employees_index") +\
            "?success=Employee+has+been+deleted.")
    except Exception as e:
        print e
        parts[19]['test_message'] = str(e)
    ##########  The deleted employee is removed from the pending table"
    try:
        parts[20]['success'] = not test.element_exists(\
            "#tab-body-approved-employees div#%s a" %(emp.objectId,))
    except Exception as e:
        print e
        parts[20]['test_message'] = str(e)
    ##########  The employee is deleted from parse"
    try:
        store.set("employees", None)
        parts[21]['success'] = store.get("employees", 
            objectId=emp.objectId, count=1) == 0
    except Exception as e:
        print e
        parts[21]['test_message'] = str(e)
    ##########  The account/user is deleted from parse"
    try:
        parts[22]['success'] = Account.objects().count(\
            username=username, email=email) == 0
    except Exception as e:
        print e
        parts[22]['test_message'] = str(e)
    ##########  Multiple employees (4) registering at once
    ###         shows up in dashboard"
    try:
        for i in range(3):
            register_employee(first_name + str(i), last_name + str(i))
        sleep(COMET_PULL_RATE*2 + 3)
        test.find("#tab-pending-employees").click()
        parts[23]['success'] = len(test.find(\
            "#tab-body-pending-employees div.tr " +\
            "div.td.approve a.approve", multiple=True)) == 3
    except Exception as e:
        print e
        parts[23]['test_message'] = str(e)
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
    
    
TEST_EMPLOYEE = {
    "username": "employee@vandolf.com",
    "password": "123456",
    "first_name": "Vandolf",
    "last_name": "Estrellado",
}

MESSAGE_DETAIL_RE = re.compile(r"messages/(.*)/details")
    
def test_employee_access():
    """
    Tests for employee dashboard access.
    This tests any user with ACL of ACCESS_PUNCHREDEEM and NO_ACCESS.
    Tests for ACCESS_ADMIN are not necessary since all other tests
    involving the store owner covers it.
    """
    
    # delete the employees and associated User objects in the relation
    account = Account.objects().get(email=TEST_USER['username'],
        include="Store.Settings")
    store = account.store
    settings = store.settings
    
    emps = store.get("employees")
    if emps:
        for emp in emps:
            Account.objects().get(Employee=emp.objectId).delete()
            emp.delete()
    store.set("employees", None) 
        
    test = SeleniumTest()
    parts = [
        {"test_name" : "Pending employee has no access"},
        {"test_name" : "Approved employee initially not in store ACL"},
        {"test_name" : "Employee with ACCESS_NONE cannot login " +\
            "using  the login dialog"},
        {"test_name" : "Employee with ACCESS_NONE cannot login " +\
            "using the dedicated login page"},
        {"test_name" : "Employee with ACCESS_PUNCHREDEEM can " +\
            "login to the dashboard through the login dialog"},
        {"test_name" : "Employee with ACCESS_PUNCHREDEEM can " +\
            "login to the dashboard through the dedicated dialog pg"},
            
        {"test_name" : "Account settings accessible"},
        {"test_name" : "No store edit button"},
        {"test_name" : "Requesting edit store detail through url " +\
            "redirects user to store index"},
        {"test_name" : "No update subscription button"},
        {"test_name" : "Requesting update subscription through url " +\
            "redirects user to store index"},
        {"test_name" : "No deactivate my store button"},
        {"test_name" : "Requesting store deactivation through url " +\
            "redirects user to store index"},
            
        {"test_name" : "Rewards accessible"},
        {"test_name" : "No create new reward button"},
        {"test_name" : "Requesting create new reward through url " +\
            "redirects user to rewards index"},
        {"test_name" : "Rewards are not clickable"},
        {"test_name" : "Requesting edit reward through url " +\
            "redirects user to rewards index"},
            
        {"test_name" : "Messages accessible"},
        {"test_name" : "No create new message button"},
        {"test_name" : "Requesting create new message through url " +\
            "redirects user to messages index"},
        {"test_name" : "Sent messages are viewable"},
        {"test_name" : "Feedbacks are viewable"},
        {"test_name" : "No reply button"},
        {"test_name" : "Requesting reply through url " +\
            "redirects user to messages index"},
        {"test_name" : "No delete message button"},
        {"test_name" : "Requesting delete message through url " +\
            "redirects user to messages index"}, 
        
        {"test_name" : "Analysis accessible"},
        
        {"test_name" : "Employees accessible"},
        {"test_name" : "No register new employee button"},
        {"test_name" : "Requesting new employee registration"+\
            "redirects user to employees_index"},
        {"test_name" : "Approved employees are not clickable"},
        {"test_name" : "Requesting edit employee through url " +\
            "redirects user to employees index"},
        {"test_name" : "No remove button in approved employees"},
        {"test_name" : "Requesting remove employee through url " +\
            "redirects user to employees index"},
        {"test_name" : "No deny button in pending employees"},
        {"test_name" : "Requesting deny employee through url " +\
            "redirects user to employees index"},
        {"test_name" : "No approve button in pending employees"},
        {"test_name" : "Requesting approve employee through url " +\
            "redirects user to employees index"},
        
        {"test_name" : "Settings accessible"},
        {"test_name" : "No refresh button for retailer pin"},
        {"test_name" : "Requesting refresh through url returns " +\
            "a json object with error Permission denied"},
        {"test_name" : "Punches employee is readonly"},
        {"test_name" : "Punches facebook is readonly"},
        {"test_name" : "No save button"},
        {"test_name" : "No cancel changes button"},
            
        {"test_name" : "Workbench accessible"},
        {"test_name" : "Employee can punch"},
        {"test_name" : "Employee can reject redeem"},
        {"test_name" : "Employee can validate redeem"},
        
    ]
    section = {
        "section_name":\
            "Employee dashboard access working as expected?",
        "parts": parts,
    }
    test.results.append(section)
    
    try:
        # register the test employee
        register_employee("employee", "ex", TEST_EMPLOYEE['username'],
            TEST_EMPLOYEE['username'], TEST_EMPLOYEE['password'],
            settings.retailer_pin)
        sleep(3)
        employee_acc = Account.objects().get(username=TEST_EMPLOYEE[\
            'username'], include="Employee")
        employee = employee_acc.employee
    except Exception as e:
        print e
        
    ##########  Pending employee has no access 
    try:
        test.login(TEST_EMPLOYEE['username'], TEST_EMPLOYEE['password'],
            reverse("employees_index"))
        parts[0]['success'] =\
            test.find("#dialog-login-message").text ==\
            "You are not yet approved."
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
        
    try:
        # login to approve
        test.login(TEST_USER['username'], TEST_USER['password'],
            reverse("employees_index"))
        # approve
        test.find("#tab-pending-employees").click()
        approveRow = test.find("#tab-body-pending-employees " +\
            "div.tr")
        approveRow.find_element_by_css_selector(\
            "div.td.approve a.approve").click()
        sleep(1)
        test.switch_to_alert().accept()
        sleep(2)
        test.logout()
    except Exception as e:
        print e
        
    ##########  Approved employee initially not in store ACL  
    try:
        # store.ACL = None cannot retrieve Parse built-ins!
        account = Account.objects().get(email=TEST_USER['username'],
            include="Store.Settings")
        store = account.store
        parts[1]['success'] = employee_acc.objectId not in store.ACL
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
        
    ##########  Employee with ACCESS_NONE cannot login 
    ###         using the login dialog 
    try:
        test.dev_login()
        test.login(TEST_EMPLOYEE['username'],
            TEST_EMPLOYEE['password'])
        parts[2]['success'] =\
            test.find("#dialog-login-message").text ==\
            "You do not have permission to access the dashboard."
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
        
    ##########  Employee with ACCESS_NONE cannot login 
    ###         using the dedicated login page 
    try:
        test.login(TEST_EMPLOYEE['username'], TEST_EMPLOYEE['password'],
            reverse("employees_index"))
        parts[3]['success'] =\
            test.find("#dialog-login-message").text ==\
            "You do not have permission to access the dashboard."
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
        
    ### Update the store's ACL
    store.ACL = {"*": {"read": True, "write": True}}
    store.set_access_level(employee_acc, ACCESS_PUNCHREDEEM[0])
    store.update()
    
    test.new_driver(False)
        
    ##########  Employee with ACCESS_PUNCHREDEEM can 
    ###         login to the dashboard through the login dialog
    try:
        test.login(TEST_EMPLOYEE['username'], TEST_EMPLOYEE['password'],
            final_sleep=6)
        parts[4]['success'] = test.is_current_url(reverse("store_index"))
        test.logout()
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
        
    ##########  Employee with ACCESS_PUNCHREDEEM can 
    ###         login to the dashboard through the dedicated dialog page
    try:
        test.dev_login()
        test.login(TEST_EMPLOYEE['username'], TEST_EMPLOYEE['password'],
            reverse("employees_index"), final_sleep=6)
        parts[5]['success'] = test.is_current_url(reverse("employees_index"))
        sleep(4)
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
        
    ##########  Account settings accessible
    try:
        test.find("#header-right a").click()
        sleep(2)
        parts[6]['success'] = test.is_current_url(reverse("account_edit"))
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
        
    ##########  No edit store detail button
    try:
        test.open(reverse("store_index"))
        sleep(2)
        test.set_to_implicit_wait(False)
        try: 
            test.find("#store-details a[href='%s']" % (reverse("store_edit"),))
        except NoSuchElementException:
            parts[7]['success'] = True
        
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting edit store detail through url 
    ###         redirects user to store details 
    try:
        test.open(reverse("store_edit"))
        sleep(2)
        parts[8]['success'] = test.is_current_url(reverse("store_index")+\
            "?" + urlencode({'error': "Permission denied"}))
    except Exception as e:
        print e
        parts[8]['test_message'] = str(e)
        
    ##########  No update subscription button 
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#account-options a[href='%s']" %\
                (reverse("subscription_update"),))
        except NoSuchElementException:
            parts[9]['success'] = True
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting update subscription through url 
    ###         redirects user to store index 
    try:
        test.open(reverse("subscription_update"))
        sleep(2)
        parts[10]['success'] = test.is_current_url(reverse(\
            "store_index")+ "?" + urlencode({'error':\
            "Permission denied"}))
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
        
    ##########  No deactivate my store button 
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#deactivate_account")
        except NoSuchElementException:
            parts[11]['success'] = True
    except Exception as e:
        print e
        parts[11]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting store deactivation through url 
    ###         redirects user to store index
    try:
        test.open(reverse("store_deactivate"))
        sleep(2)
        parts[12]['success'] = test.is_current_url(reverse(\
            "store_index")+ "?" + urlencode({'error':\
            "Permission denied"}))
    except Exception as e:
        print e
        parts[12]['test_message'] = str(e)
        
    ##########  Rewards accessible
    try:
        test.open(reverse("rewards_index"))
        sleep(2)
        parts[13]['success'] = test.is_current_url(reverse("rewards_index"))
    except Exception as e:
        print e
        parts[13]['test_message'] = str(e)
        
    ##########  No create new reward button
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#add_reward")
        except NoSuchElementException:
            parts[14]['success'] = True
        
    except Exception as e:
        print e
        parts[14]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting create new reward through url 
    ###         redirects user to rewards index
    try:
        test.open(reverse("reward_edit", args=(-1,)))
        sleep(2)
        parts[15]['success'] = test.is_current_url(reverse(\
            "rewards_index")+ "?" + urlencode({'error':\
            "Permission denied"}))
    except Exception as e:
        print e
        parts[15]['test_message'] = str(e)
        
    ##########  Rewards are not clickable
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("div.tr.reward a")
        except NoSuchElementException:
            parts[16]['success'] = True
            
    except Exception as e:
        print e
        parts[16]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting edit reward through url 
    ###         redirects user to rewards index
    try:
        test.open(reverse("reward_edit", args=\
            (int(test.find("div.tr.reward").get_attribute("id")),)))
        sleep(3)
        parts[17]['success'] = test.is_current_url(reverse(\
            "rewards_index")+ "?" + urlencode({'error':\
            "Permission denied"}))
    except Exception as e:
        print e
        parts[17]['test_message'] = str(e)
        
    ##########  Messages accessible
    try:
        test.open(reverse("messages_index"))
        sleep(3)
        parts[18]['success'] = test.is_current_url(reverse(\
            "messages_index"))
    except Exception as e:
        print e
        parts[18]['test_message'] = str(e)
        
    ##########  No create new message button
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#create_message")
        except NoSuchElementException:
            parts[19]['success'] = True
        
    except Exception as e:
        print e
        parts[19]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting create new message through url 
    ###         redirects user to messages index
    try:
        test.open(reverse("message_edit", args=("0",)))
        sleep(3)
        parts[20]['success'] = test.is_current_url(reverse(\
            "messages_index")+ "?" + urlencode({'error':\
            "Permission denied"}))
            
    except Exception as e:
        print e
        parts[20]['test_message'] = str(e)
        
    ##########  Sent messages are viewable 
    try:
        row = test.find("#tab-body-sent div.tr a")
        # get id from /manage/messages/H1llFritVJ/details
        message_id = MESSAGE_DETAIL_RE.search(\
            row.get_attribute("href")).group(1)
        row.click()
        sleep(3)
        parts[21]['success'] = test.is_current_url(reverse(\
            "message_details", args=(message_id,)))
        
    except Exception as e:
        print e
        parts[21]['test_message'] = str(e)
        
    ##########  Feedbacks are viewable
    try:
        test.open(reverse("messages_index"))
        sleep(2)
        test.find("#tab-feedback").click()
        sleep(1)
        row = test.find("#tab-body-feedback div.tr a")
        # get id from /manage/messages/feedback/H1llFritVJ
        feedback_id = row.get_attribute("href").split("/")[-1]
        row.click()
        sleep(3)
        parts[22]['success'] = test.is_current_url(reverse(\
            "feedback_details", args=(feedback_id,)))
            
    except Exception as e:
        print e
        parts[22]['test_message'] = str(e)
        
    ##########  No reply button
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#reply-button")
        except NoSuchElementException:
            parts[23]['success'] = True
        
    except Exception as e:
        print e
        parts[23]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting reply through url 
    ###         redirects user to messages index
    try:
        test.open(reverse("feedback_reply", args=(feedback_id,)))
        sleep(3)
        parts[24]['success'] = test.is_current_url(reverse(\
            "messages_index")+ "?" + urlencode({'error':\
            "Permission denied"}) + "&tab_feedback=1")
        
    except Exception as e:
        print e
        parts[24]['test_message'] = str(e)
        
    ##########  No delete message button
    try:
        test.open(reverse("feedback_details", args=(feedback_id,)))
        sleep(3)
        test.set_to_implicit_wait(False)
        try:
            test.find("#delete-button")
        except NoSuchElementException:
            parts[25]['success'] = True
        
    except Exception as e:
        print e
        parts[25]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting delete message through url 
    ###         redirects user to messages index 
    try:
        test.open(reverse("feedback_delete", args=(feedback_id,)))
        sleep(2)
        parts[26]['success'] = test.is_current_url(reverse(\
            "messages_index")+ "?" + urlencode({'error':\
            "Permission denied"}) + "&tab_feedback=1")
            
    except Exception as e:
        print e
        parts[26]['test_message'] = str(e)
    
    ##########  Analysis accessible
    try:
        test.open(reverse("analysis_index"))
        sleep(4)
        parts[27]['success'] = test.is_current_url(reverse(\
            "analysis_index"))
            
    except Exception as e:
        print e
        parts[27]['test_message'] = str(e)
    
    ##########  Employees accessible
    try:
        test.open(reverse("employees_index"))
        sleep(4)
        parts[28]['success'] = test.is_current_url(reverse(\
            "employees_index"))
            
    except Exception as e:
        print e
        parts[28]['test_message'] = str(e)
    
    ##########  No register new employee button
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#register_employee")
        except NoSuchElementException:
            parts[29]['success'] = True
        
    except Exception as e:
        print e
        parts[29]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting new employee registration
    ###         redirects user to employees_index
    try:
        test.open(reverse("employee_register"))
        sleep(3)
        parts[30]['success'] = test.is_current_url(reverse(\
            "employees_index")+ "?" + urlencode({'error':\
            "Permission denied"}))
            
    except Exception as e:
        print e
        parts[30]['test_message'] = str(e)
        
    ##########  Approved employees are not clickable
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#tab-body-approved-employees div.tr a")
        except NoSuchElementException:
            parts[31]['success'] = True
        
    except Exception as e:
        print e
        parts[31]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting edit employee through url 
    ###         redirects user to employees index
    try:
        row = test.find("#tab-body-approved-employees div.tr")
        employee_id = row.get_attribute("id")
        test.open(reverse("employee_edit", args=(employee_id,)))
        sleep(3)
        parts[32]['success'] = test.is_current_url(reverse(\
            "employees_index")+ "?" + urlencode({'error':\
            "Permission denied"}))

    except Exception as e:
        print e
        parts[32]['test_message'] = str(e)
        
    ##########  No remove button in approved employees
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#tab-body-approved-employees div.tr "+\
                "div.remove a")
        except NoSuchElementException:
            parts[33]['success'] = True
        
    except Exception as e:
        print e
        parts[33]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting remove employee through url 
    ###         redirects user to employees index
    try:
        test.open(reverse("employee_delete", args=(employee_id,)))
        sleep(3)
        parts[34]['success'] = test.is_current_url(reverse(\
            "employees_index")+ "?" + urlencode({'error':\
            "Permission denied"}))
        
    except Exception as e:
        print e
        parts[34]['test_message'] = str(e)
        
    
    # create a pending 
    register_rand_employee(store.objectId)
    test.new_driver(False)
    test.login(TEST_EMPLOYEE['username'], TEST_EMPLOYEE['password'],
        reverse("employees_index"), final_sleep=6)
        
    ##########  No deny button in pending employees
    try:
        test.find("#tab-pending-employees").click()
        sleep(1)
        test.set_to_implicit_wait(False)
        try:
            test.find("#tab-body-pending-employees div.tr "+\
                "div.deny a")
        except NoSuchElementException:
            parts[35]['success'] = True
            
    except Exception as e:
        print e
        parts[35]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting deny employee through url 
    ###         redirects user to employees index
    try:
        test.find("#tab-pending-employees").click()
        row = test.find("#tab-body-pending-employees div.tr")
        employee_id = row.get_attribute("id")
        test.open(reverse("employee_deny", args=(employee_id,)))
        sleep(3)
        parts[36]['success'] = test.is_current_url(reverse(\
            "employees_index") + "?" + urlencode({'error':\
            "Permission denied"}))
            
    except Exception as e:
        print e
        parts[36]['test_message'] = str(e)
        
    ##########  No approve button in pending employees
    try:
        test.find("#tab-pending-employees").click()
        sleep(1)
        test.set_to_implicit_wait(False)
        try:
            test.find("#tab-body-pending-employees div.tr "+\
                "div.approve a")
        except NoSuchElementException:
            parts[37]['success'] = True
            
    except Exception as e:
        print e
        parts[37]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting approve employee through url 
    ###         redirects user to employees index 
    try:
        test.open(reverse("employee_approve", args=(employee_id,)))
        sleep(3)
        parts[38]['success'] = test.is_current_url(reverse(\
            "employees_index") + "?" + urlencode({'error':\
            "Permission denied"}))
            
    except Exception as e:
        print e
        parts[38]['test_message'] = str(e)
    
    ##########  Settings accessible
    try:
        test.open(reverse("store_settings"))
        sleep(3)
        parts[39]['success'] = test.is_current_url(reverse(\
            "store_settings"))
            
    except Exception as e:
        print e
        parts[39]['test_message'] = str(e)
        
    ##########  No refresh button for retailer pin
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#link_refresh_retailer_pin")
        except NoSuchElementException:
            parts[40]['success'] = True
        
    except Exception as e:
        print e
        parts[40]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Requesting refresh through url returns 
    ###         a json object with error Permission denied
    try:
        test.open(reverse("refresh_retailer_pin"))
        sleep(3)
        parts[41]['success'] = "Permission denied" in\
            test.driver.page_source
    except Exception as e:
        print e
        parts[41]['test_message'] = str(e)
        
    ##########  Punches employee is readonly
    try:
        test.open(reverse("store_settings"))
        sleep(3)
        parts[42]['success'] =\
            test.find("#id_punches_employee").get_attribute(\
                "readonly") == "true"
    except Exception as e:
        print e
        parts[42]['test_message'] = str(e)
        
    ##########  Punches facebook is readonly
    try:
        parts[43]['success'] =\
            test.find("#id_punches_facebook").get_attribute(\
                "readonly") == "true"
    except Exception as e:
        print e
        parts[43]['test_message'] = str(e)
        
    ##########  No save button
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#settings-form-submit")
        except NoSuchElementException:
            parts[44]['success'] = True
        
    except Exception as e:
        print e
        parts[44]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  No cancel changes button
    try:
        test.set_to_implicit_wait(False)
        try:
            test.find("#settings-options a.red")
        except NoSuchElementException:
            parts[45]['success'] = True
            
    except Exception as e:
        print e
        parts[45]['test_message'] = str(e)
    finally:
        test.set_to_implicit_wait(True)
        
    ##########  Workbench accessible
    try:
        test.open(reverse("workbench_index"))
        sleep(3)
        parts[46]['success'] = test.is_current_url(\
            reverse("workbench_index"))
    except Exception as e:
        print e
        parts[46]['test_message'] = str(e)
        
    ##########  Employee can punch
    try:
        test.find("#punch_code").send_keys("00010")
        test.find("#punch_amount").send_keys("1")
        test.find("#punch-form a.button.blue").click()
        sleep(2)
        parts[47]['success'] =\
            test.find(".notification.hide") is not None
    except Exception as e:
        print e
        parts[47]['test_message'] = str(e)
        
    ##########  Employee can reject redeem 
    try:
        request_redeem_ps("eiZa6Mzu7f")
        sleep(COMET_PULL_RATE*2+4)
        row = test.find("#tab-body-pending-redemptions div.tr")
        test.find("//div[@id='%s']/" % (row.get_attribute("id"),) +\
            "div[contains(@class, 'redemption_redeem')]/a[2]",
            type="xpath").click()
        sleep(3)
        parts[48]['success'] = row.text.__contains__("Successfully")
    except Exception as e:
        print e
        parts[48]['test_message'] = str(e)
        
    ##########  Employee can validate redeem
    try:
        request_redeem_ps("eiZa6Mzu7f")
        sleep(COMET_PULL_RATE*2+4)
        row = test.find("#tab-body-pending-redemptions div.tr")
        test.find("//div[@id='%s']/" % (row.get_attribute("id"),) +\
            "div[contains(@class, 'redemption_redeem')]/a[1]",
            type="xpath").click()
        sleep(3)
        parts[49]['success'] = row.text.__contains__("Successfully")
    except Exception as e:
        print e
        parts[49]['test_message'] = str(e)


    # END OF ALL TESTS - cleanup
    return test.tear_down() 

def test_employee_registration():
    """
    Tests for employee registrain via dashboard.
    """
    # delete the employees and associated User objects in the relation
    account = Account.objects().get(email=TEST_USER['username'],
        include="Store.Settings")
    store = account.store
    settings = store.settings
    
    emps = store.get("employees")
    if emps:
        for emp in emps:
            Account.objects().get(Employee=emp.objectId).delete()
            emp.delete()
    store.set("employees", None) 
        
    test = SeleniumTest()
    parts = [
        {"test_name" : "Clicking register new employee button "+\
            " redirects user to employee register page."},
        {"test_name" : "New registered employee is immediately placed"+\
            " in the approved group."},
        {"test_name" : "Access level of new employee is the same as"+\
            " the one chosen in the registration form."},
            
        {"test_name" : "A valid email is required."},
        {"test_name" : "Email must be unique."},
        
        {"test_name" : "Email is required."},
        {"test_name" : "First name is required."},
        {"test_name" : "Last name is required."},
        {"test_name" : "Password is required."},
        {"test_name" : "Password confirm is required."},
        
        {"test_name" : "Passwords must match."},
        {"test_name" : "Password must be at least 6 characters long."},
        
    ]
    section = {
        "section_name":\
            "Employee registration functional?",
        "parts": parts,
    }
    test.results.append(section)

    test.login(TEST_USER['username'], TEST_USER['password'],
        reverse("employees_index"))
    
    ##########  Clicking register new employee button 
    ###         redirects user to employee register page.
    try:
        test.find("#register_employee").click()
        sleep(3)
        parts[0]['success'] = test.is_current_url(reverse("employee_register"))
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    
    ##########  New registered employee is immediately placed
    ###         in the approved group.
    try:
        acl = test.find("#id_acl option[selected]").get_attribute("value")
        
        selectors = (
            ("#id_email", TEST_EMPLOYEE['username']),
            ("#id_password", TEST_EMPLOYEE['password']),
            ("#id_confirm_password", TEST_EMPLOYEE['password']),
            ("#id_first_name", TEST_EMPLOYEE['first_name']),
            ("#id_last_name", TEST_EMPLOYEE['last_name']),
        )
        test.action_chain(0, selectors, action="send_keys")
        test.find("#register-employee-submit").click()
        sleep(7)
        test.open(reverse("employees_index"))
        sleep(3)
        parts[1]['success'] = test.find("#tab-body-approved-employees"+\
            " div.tr a div.td.first_name_approved").text ==\
            TEST_EMPLOYEE['first_name']
        
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
    
    ##########  Access level of new employee is the same as
    ###         the one chosen in the registration form.
    try:
        test.find("#tab-body-approved-employees div.tr a").click()
        sleep(2)
        parts[2]['success'] = acl ==\
            test.find("#ACL option[selected]").get_attribute("value")
    
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
        
    ##########  A valid email is required.
    try:
        test.open(reverse("employee_register"))
        sleep(2)
        test.find("#id_email").send_keys("jhfghjdfg@jfgh")
        test.find("#register-employee-submit").click()
        sleep(3)
        parts[3]['success'] = test.find("#email_ic > ul.errorlist > li").text ==\
            "Enter a valid email address."
        
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)    
    
    ##########  Email must be unique.
    try:
        selectors = (
            ("#id_email", TEST_EMPLOYEE['username']),
            ("#id_password", "123456123"),
            ("#id_confirm_password", "123456123"),
            ("#id_first_name", "YOLO"),
            ("#id_last_name", "BOLO"),
        )
        test.action_chain(0, selectors, action="clear")
        test.action_chain(0, selectors, action="send_keys")
        test.find("#register-employee-submit").click()
        sleep(5)
        parts[4]['success'] = test.find("#email_ic > ul.errorlist > li").text ==\
            "Email is already being used."
            
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
    
    ##########  Email is required.              5
    ##########  First name is required.         6
    ##########  Last name is required.          7
    ##########  Password is required.           8
    ##########  Password confirm is required.   9
    try:
        selectors = (
            "#id_email", 
            "#id_password",
            "#id_confirm_password",
            "#id_first_name",
            "#id_last_name",
        )
        test.action_chain(0, selectors, action="clear")
        test.find("#register-employee-submit").click()
        sleep(3)
        
        for i, sel in enumerate(selectors):
            id = sel.replace("#id_", "") + "_ic"
            parts[i+5]['success'] =\
                test.find("#%s > ul.errorlist > li" % (id,)).text ==\
                "This field is required."
        
    except Exception as e:
        print e
        for i, sel in enumerate(selectors):
            parts[i+5]['test_message'] = str(e)
    
    ##########  Passwords must match.
    try:
        selectors = (
            ("#id_password", "123456"),
            ("#id_confirm_password", "abcdefg"),
        )
        test.action_chain(0, selectors, action="clear")
        test.action_chain(0, selectors, action="send_keys")
        test.find("#register-employee-submit").click()
        sleep(3)
        parts[10]['success'] = test.find("#password_ic > ul.errorlist > li").text ==\
            "Passwords don't match."
        
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
    
    ##########  Password must be at least 6 characters long.
    try:
        test.find("#id_password").clear()
        test.find("#id_password").send_keys("123")
        test.find("#register-employee-submit").click()
        sleep(3)
        parts[11]['success'] =\
            test.find("#password_ic > ul.errorlist > li").text ==\
            "Ensure this value has at least 6 characters (it has 3)."
        
    except Exception as e:
        print e
        parts[11]['success'] = str(e)


    # END OF ALL TESTS - cleanup
    return test.tear_down() 


