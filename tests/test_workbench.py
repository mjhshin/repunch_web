"""
Selenium tests for dashboard 'Workbench' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest
from parse.apps.accounts.models import Account

TEST_USER = {
    "username": "violette87@repunch.com",
    "password": "repunch7575",
}

def test_punch():
    """
    Tests for punch customers section of the workbench.

    Assumes that at least 1 PatronStore exists for the above Account.
    """
    # retrieve a patronstore
    account = Account.objects().get(username=TEST_USER['username'],
        include="Store.Settings")
    store = account.store
    settings = store.settings
    ps = store.get("patronStores", include="Patron", limit=1)[0]
    patron = ps.patron
    
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Punching works"},
        {'test_name': "PatronStore punch_count is updated"},
        {'test_name': "PatronStore all_time_punches is updated"},
        {'test_name': "Punch Code is required"},
        {'test_name': "Punch Codes consist of only numbers"},
        {'test_name': "Punch Codes are 5 characters long"},
        {'test_name': "Amount of punches is required"},
        {'test_name': "Amount should not exceed maximum employee punches allowed"},
        {'test_name': "Amount must be greater than 0"},
        {'test_name': "Non-existent Punch Code shows approprirate message"},
    ]
    section = {
        "section_name": "Punch working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("workbench_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("workbench_index"))
        
    # login
    selectors = (
        ("#login_username", TEST_USER['username']),
        ("#login_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(5) 
    
    def punch(punch_code="", punch_amount="", sleep_prior=0,
        sleep_after=0):
        if sleep_prior > 0:
            sleep(sleep_prior)
        test.find("#punch_code").clear()
        test.find("#punch_amount").clear()
        test.find("#punch_code").send_keys(punch_code)
        test.find("#punch_amount").send_keys(punch_amount)
        test.find("#punch-form a.button.blue").click()
        if sleep_after > 0:
            sleep(sleep_after)
        
    ##########  Punching works
    try:
        punch_count, all_time_punches =\
            ps.punch_count, ps.all_time_punches
        
        punch(patron.punch_code, "1", sleep_after=3)
        parts[1]['success'] =\
            test.find("#punch-notification") is not None
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
        
    ##########  PatronStore punch_count is updated
    try:
        ps.punch_count = None
        parts[2]['success'] = punch_count+1 == ps.get("punch_count")
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
        
    ##########  PatronStore all_time_punches is updated
    try:
        ps.all_time_punches = None
        parts[3]['success'] =\
            all_time_punches+1 == ps.get("all_time_punches")
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
        
    ##########  Punch Code is required
    try:
        punch(sleep_prior=5, sleep_after=1)
        parts[4]['success'] =\
            test.find("#punch-notification").text ==\
            "Please enter the customer's punch code."
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
        
    ##########  Punch Codes consist of only numbers
    try:
        punch("123ab", sleep_prior=5, sleep_after=1)
        parts[5]['success'] =\
            test.find("#punch-notification").text ==\
            "Punch Codes consist of only numbers."
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
        
    ##########  Punch Codes are 5 characters long
    try:
        punch("123", sleep_prior=5, sleep_after=1)
        parts[6]['success'] =\
            test.find("#punch-notification").text ==\
            "Punch Codes are 5 characters long."
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
        
    ##########  Amount of punches is required
    try:
        punch(patron.punch_code, sleep_prior=5, sleep_after=1)
        parts[7]['success'] =\
            test.find("#punch-notification").text ==\
            "Please enter the number of punches to give."
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
        
    ##########  Amount should not exceed maximum employee punches allowed
    try:
        punch(patron.punch_code, str(settings.punches_employee+1),
            sleep_prior=5, sleep_after=1)
        parts[8]['success'] =\
            test.find("#punch-notification").text ==\
            "Maximum amount of punches is %s." % (str(settings.punches_employee),)
    except Exception as e:
        print e
        parts[8]['test_message'] = str(e)
        
    ##########  Amount must be greater than 0
    try:
        punch(patron.punch_code, "-1", sleep_prior=5, sleep_after=1)
        parts[9]['success'] =\
            test.find("#punch-notification").text ==\
            "Amount of punches must be greater than 0."
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
        
    ##########  Non-existent Punch Code shows approprirate message
    try:
        punch("39393", "1", sleep_prior=5, sleep_after=1)
        parts[10]['success'] =\
            test.find("#punch-notification").text ==\
            "A customer with that Punch Code was not found."
        pass 
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
    
def test_redemptions():
    """
    Tests for redemptions section of the workbench.
    """
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Approving redeem works"},
        {'test_name': "Rejecting redeem works"},
        {'test_name': "Approved redeem is in the history tab"},
        {'test_name': "Rejected redeem is not in the history tab"},
        {'test_name': "Approving a redeem when the PatronStore does" +\
            " not have enough punches shows error"},
        {'test_name': "Approving redeem from a PatronStore that does" +\
            " not exist shows error"},
    ]
    section = {
        "section_name": "Redeems working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("workbench_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("workbench_index"))
        
    # login
    selectors = (
        ("#login_username", TEST_USER['username']),
        ("#login_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(5) 
        
    ##########  Approving redeem works TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
        
    ##########  Rejecting redeem works TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
        
    ##########  Approved redeem is in the history tab TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
        
    ##########  Rejected redeem is not in the history tab TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
        
    ##########  Approving a redeem when the PatronStore does
    ###         not have enough punches shows error TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
        
    ##########  Approving redeem from a PatronStore that does
    ###         not exist shows error TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
        
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
