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
    "username": "clothing",
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
        {'test_name': "Approving 2 employees in succession works"},
        {'test_name': "Removing 2 employees in succession works"},
        {'test_name': "Denying 2 employees in succession works"},
    ]
    section = {
        "section_name": "Employees page working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    print "User needs to be logged in to access page"
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
        
    def approve():
        """ 
        Approves the first pending employee on the table.
        Also returns the employee id.
        """
        print "APPROVED"
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
        print "DENYING"
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
        print "REMOVING"
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
    "vandolf1", "estrellado", "xmanvmanx", "xmanvman@xman.com"
        
    print "Cloud code register_employee works"
    try:
        res = register_employee(first_name, last_name, username,
            email=email)
        parts[1]['success'] = res.get("result") == "success"
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
    print "Employee is saved in store's Employees relation"
    try:
        emp = store.get("employees")[0]
        parts[2]['success'] = emp is not None
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
    print "Employee is initially pending (Parse)"
    try:
        parts[3]['success'] = emp.status == PENDING
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
    print "Employee is initially pending (Dashboard)"
    try:
        sleep(COMET_PULL_RATE*2 + 1) # wait for dashboard to receive
        test.find("#tab-pending-employees").click()
        parts[4]['success'] = test.element_exists(\
            "#tab-body-pending-employees ")
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
    print "Email must be valid (cloud code)"
    try:
        res = register_employee("vman", "vman", email="vmahs@vman")
        parts[5]['success'] = res['error'] == '125'
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
    print "Email must be unique (cloud code) "
    try:
        res = register_employee("vman", "vman",
            email=email)
        parts[6]['success'] = res['error'] == '203'
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
    print "Username must be unique (cloud code) "
    try:
        res = register_employee("vman", "vman", username=username)
        parts[7]['success'] = res['error'] == '202'
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
    print "Retailer PIN must exist (cloud code) "
    try:
        res = register_employee("vman", "vman", retailer_pin="sdgdgs")
        parts[8]['success'] = res['result'] == "invalid_pin"
    except Exception as e:
        print e
        parts[8]['test_message'] = str(e)
    print "Clicking deny prompts the user to confirm"
    try:
        test.find("#tab-pending-employees").click()
        test.find("#tab-body-pending-employees div.tr " +\
            "div.td.approve a.deny").click()
        alert = test.switch_to_alert()
        parts[9]['success'] = alert.text == "Deny employee?"
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
    print "The user is redirected to employee index"
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
    print "The denied employee is removed from the pending table"
    try:
        parts[11]['success'] = not test.element_exists(\
        "#tab-body-pending-employees div.tr " +\
            "div.td.approve a.approve")
    except Exception as e:
        print e
        parts[11]['test_message'] = str(e)
    print "The employee is deleted from parse"
    try:
        store.set("employees", None)
        parts[12]['success'] = store.get("employees",\
            first_name=first_name, last_name=last_name, count=1) == 0
    except Exception as e:
        print e
        parts[12]['test_message'] = str(e)
    print "The account/user is deleted from parse"
    try:
        parts[13]['success'] = Account.objects().count(\
            username=username, email=email) == 0
    except Exception as e:
        print e
        parts[13]['test_message'] = str(e)
    print "Approving the employee moves it from pending to approved"
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
    print "Employee status is set to approved in Parse"
    try:
        store.set("employees", None)
        emp = store.get("employees", first_name=first_name,
            last_name=last_name)[0]
        parts[15]['success'] = emp.status == APPROVED
    except Exception as e:
        print e
        parts[15]['test_message'] = str(e)
    print "Employee initially has 0 punches"
    try:
        parts[16]['success'] = emp.lifetime_punches == 0
    except Exception as e:
        print e
        parts[16]['test_message'] = str(e)
    print "Clicking on the approved employee row " +\
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
    print "Clicking delete prompts the user to confirm"
    try:
        test.find("#delete-button").click()
        alert = test.switch_to_alert()
        parts[18]['success'] = alert.text ==\
            "Are you sure you want to delete this employee?"
    except Exception as e:
        print e
        parts[18]['test_message'] = str(e)
    print "The user is redirected to employee index"
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
    print "The deleted employee is removed from the pending table"
    try:
        parts[20]['success'] = not test.element_exists(\
            "#tab-body-approved-employees div#%s a" %(emp.objectId,))
    except Exception as e:
        print e
        parts[20]['test_message'] = str(e)
    print "The employee is deleted from parse"
    try:
        store.set("employees", None)
        parts[21]['success'] = store.get("employees", 
            objectId=emp.objectId, count=1) == 0
    except Exception as e:
        print e
        parts[21]['test_message'] = str(e)
    print "The account/user is deleted from parse"
    try:
        parts[22]['success'] = Account.objects().count(\
            username=username, email=email) == 0
    except Exception as e:
        print e
        parts[22]['test_message'] = str(e)
    print "Multiple employees (4) registering at once " +\
        "shows up in dashboard"
    try:
        for i in range(4):
            register_employee(first_name + str(i), last_name + str(i))
        sleep(COMET_PULL_RATE*2 + 2)
        parts[23]['success'] = len(test.find(\
            "#tab-body-pending-employees div.tr " +\
            "div.td.approve a.approve", multiple=True)) == 4
    except Exception as e:
        print e
        parts[23]['test_message'] = str(e)
    print "Approving 2 employees in succession works"
    try:
        success = True
        for i in range(2):
            emp_id = approve()
            # now check if the row is in the approved table and no
            # longer in the pending table
            test.find("#tab-approved-employees").click()
            if not test.element_exists(\
                "#tab-body-approved-employees div#%s a" % (emp_id,)):
                success = False
                break
            test.find("#tab-pending-employees").click()
            if test.element_exists(\
                "#tab-body-pending-employees div#%s a" % (emp_id,)):
                success = False
                break
                
        parts[24]['success'] = success
    except Exception as e:
        print e
        parts[24]['test_message'] = str(e)
    print "Removing 2 employees in succession works"
    try:
        success = True
        for i in range(2):
            emp_id = remove()
            print emp_id
            # now check if the row is no longer in the pending table
            # and also not the approved table
            test.find("#tab-approved-employees").click()
            if test.element_exists(\
                "#tab-body-approved-employees div#%s a" % (emp_id,)):
                success = False
                break
            test.find("#tab-pending-employees").click()
            if test.element_exists(\
                "#tab-body-pending-employees div#%s a" % (emp_id,)):
                success = False
                break
                
        parts[25]['success'] = success
    except Exception as e:
        print e
        parts[25]['test_message'] = str(e)
    print "Denying 2 employees in succession works"
    try:
        success = True
        for i in range(2):
            emp_id = deny()
            # now check if the row is no longer in the pending table
            # and also not the approved table
            test.find("#tab-approved-employees").click()
            if test.element_exists(\
                "#tab-body-approved-employees div#%s a" % (emp_id,)):
                success = False
                break
            test.find("#tab-pending-employees").click()
            if test.element_exists(\
                "#tab-body-pending-employees div#%s a" % (emp_id,)):
                success = False
                break
                
        parts[26]['success'] = success
    except Exception as e:
        print e
        parts[26]['test_message'] = str(e)
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
