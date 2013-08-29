"""
Selenium tests for dashboard 'Employees' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest
from parse.utils import cloud_call
from parse.apps.accounts.models import Account
from parse.apps.employees import PENDING, APPROVED
from repunch.settings import COMET_PULL_RATE

TEST_USER = {
    "username": "clothing@vandolf.com",
    "password": "123456",
}

def test_employees():
    """
    Tests for employee approve, deny, remove, details. etc.
    """
    # TODO test employee graph
    
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
        {'test_name': "Multiple employees (4) registering at once" +\
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
        
    def approve():
        """ 
        Approves the first pending employee on the table.
        Also returns the employee id.
        """
        test.find("#tab-pending-employees").click()
        approveRow = test.find("#tab-body-pending-employees " +\
            "div.tr")
        approveId = approveRow.get_attribute("id")
        approveRow.find_element_by_css_selector(\
            "div.td.approve a.approve").click()
        sleep(1)
        test.switch_to_alert().accept()
        sleep(2)
        return approveId
        
    def deny(): 
        """ 
        Denies the first pending employee on the table.
        Also returns the employee id.
        """
        test.find("#tab-pending-employees").click()
        denyRow = test.find("#tab-body-pending-employees " +\
            "div.tr")
        denyId = denyRow.get_attribute("id")
        denyRow.find_element_by_css_selector(\
            "div.td.approve a.deny").click()
        sleep(1)
        test.switch_to_alert().accept()
        sleep(3)
        return denyId
        
    def remove():
        """
        Removes the first approved employee on the table.
        Also returns the employee id.
        """
        test.find("#tab-approved-employees").click()
        removeRow = test.find("#tab-body-approved-employees " +\
            "div.tr")
        removeId = removeRow.get_attribute("id")
        removeRow.find_element_by_css_selector("div.td.remove a").click()
        sleep(1)
        test.switch_to_alert().accept()
        sleep(3)
        return removeId
        
    first_name, last_name, username, email =\
    "vandolf1", "estrellado", "xmanvman@xman.com", "xmanvman@xman.com"
        
    ##########  Cloud code register_employee works"
    try:
        res = register_employee(first_name, last_name, username,
            email=email)
        parts[1]['success'] = res.get("result") == "success"
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
            "#tab-body-pending-employees ")
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
    ##########  Email must be valid (cloud code)"
    try:
        res = register_employee("vman", "vman", email="vmahs@vman")
        parts[5]['success'] = res['error'] == '125'
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
    ##########  Email must be unique (cloud code) "
    try:
        res = register_employee("vman", "vman",
            email=email)
        parts[6]['success'] = res['error'] == '203'
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
    ##########  Username must be unique (cloud code) "
    try:
        res = register_employee("vman", "vman", username=username)
        parts[7]['success'] = res['error'] == '202'
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
    ##########  Retailer PIN must exist (cloud code) "
    try:
        res = register_employee("vman", "vman", retailer_pin="sdgdgs")
        parts[8]['success'] = res['result'] == "invalid_pin"
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
        approve()
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
    ##########  Clicking on the approved employee row " +\
        "redirects user to employee edit page "
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
    ##########  Multiple employees (4) registering at once " +\
        "shows up in dashboard"
    try:
        for i in range(4):
            register_employee(first_name + str(i), last_name + str(i))
        sleep(COMET_PULL_RATE*2 + 3)
        parts[23]['success'] = len(test.find(\
            "#tab-body-pending-employees div.tr " +\
            "div.td.approve a.approve", multiple=True)) == 4
    except Exception as e:
        print e
        parts[23]['test_message'] = str(e)
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
    
    
TEST_EMPLOYEE = {
    "username": "employee@vandolf.com",
    "password": "123456",
}
    
def test_employee_access():
    """
    Tests for employee dashboard access.
    This tests any user with ACL of ACCESS_PUNCHREDEEM and NO_ACCESS.
    Tests for ACCESS_ADMIN are not necessary since all other tests
    involving the store owner covers it.
    """
    
    # delete the employees and associated User objects in the relation
    account = Account.objects().get(email=TEST_USER['email'],
        include="Store.Settings")
    store = account.store
    settings = store.settings
    
    emps = store.get("employees")
    if emps:
        for emp in emps:
            Account.objects().get(Employee=emp.objectId).delete()
            emp.delete()
    store.set("employees", None) 
    
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
        
    # register the test employee
    register_employee("employee", "empy", username=TEST_EMPLOYEE[\
        'username'], email=TEST_EMPLOYEE[\
        'username'], password=TEST_EMPLOYEE['password'])
    
    test = SeleniumTest()
    parts = [
        {"test_name" : "Pending employee has no access"},
        {"test_name" : "Approved employee initially has no access"},
        {"test_name" : "Employee with ACCESS_NONE cannot login " +\
            "using  the login dialog"},
        {"test_name" : "Employee with ACCESS_NONE cannot login " +\
            "using the dedicated login page"},
        {"test_name" : "Employee with ACCESS_PUNCHREDEEM can " +\
            "login to the dashboard through the login dialog"},
        {"test_name" : "Employee with ACCESS_PUNCHREDEEM can " +\
            "login to the dashboard through the dedicated dialog pg"},
            
        {"test_name" : "My Account accessible"},
        {"test_name" : "No edit store detail button"},
        {"test_name" : "Requesting edit store detail through url " +\
            "redirects user to store details"},
        {"test_name" : "No update account button"},
        {"test_name" : "Requesting update account through url " +\
            "redirects user to store details"},
        {"test_name" : "No cancel my account button"},
        {"test_name" : "Requesting cancel my account through url " +\
            "redirects user to store details"},
            
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
    
    ##########  User needs to be logged in to access page
    test.open(reverse("employees_index")) # ACTION!
    sleep(1)
        
    # login
    selectors = (
        ("#login_username", TEST_EMPLOYEE['username']),
        ("#login_password", TEST_EMPLOYEE['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(5) 
    
    
    ##########  Pending employee has no access  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Approved employee initially has no access  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Employee with ACCESS_NONE cannot login 
    ###         using  the login dialog  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Employee with ACCESS_NONE cannot login 
    ###         using the dedicated login page  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Employee with ACCESS_PUNCHREDEEM can 
    ###         login to the dashboard through the login dialog  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Employee with ACCESS_PUNCHREDEEM can 
    ###         login to the dashboard through the dedicated dialog pg  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
        
    ##########  My Account accessible  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No edit store detail button  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting edit store detail through url 
    ###         redirects user to store details  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No update account button  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting update account through url 
    ###         redirects user to store details  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No cancel my account button  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting cancel my account through url 
    ###         redirects user to store details  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
        
    ##########  Rewards accessible  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No create new reward button  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting create new reward through url 
    ###         redirects user to rewards index  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Rewards are not clickable  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting edit reward through url 
    ###         redirects user to rewards index  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
        
    ##########  Messages accessible  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No create new message button  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting create new message through url 
    ###         redirects user to messages index  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Sent messages are viewable  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Feedbacks are viewable  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No reply button  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting reply through url 
    ###         redirects user to messages index  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No delete message button  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting delete message through url 
    ###         redirects user to messages index  TODO 
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    
    ##########  Analysis accessible  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    
    ##########  Employees accessible  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Approved employees are not clickable  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting edit employee through url 
    ###         redirects user to employees index  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No remove button in approved employees  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting remove employee through url 
    ###         redirects user to employees index  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No deny button in pending employees  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting deny employee through url 
    ###         redirects user to employees index  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No approve button in pending employees  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting approve employee through url 
    ###         redirects user to employees index  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    
    ##########  Settings accessible  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No refresh button for retailer pin  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Requesting refresh through url returns 
    ###         a json object with error Permission denied  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Punches employee is readonly  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Punches facebook is readonly  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No save button  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  No cancel changes button  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
        
    ##########  Workbench accessible  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Employee can punch  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Employee can reject redeem  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)
    ##########  Employee can validate redeem  TODO
    try:
        pass
    except Exception as e:
        print e
        parts[0]['test_message'] = str(e)







