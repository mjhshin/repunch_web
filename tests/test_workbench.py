"""
Selenium tests for dashboard 'Workbench' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest

TEST_USER = {
    "username": "violette87@repunch.com",
    "password": "repunch7575",
}

def test_punch():
    """
    Tests for punch customers section of the workbench.
    """
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Punching works"},
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
    
    ##########  User needs to be logged in to access page TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
        
    ##########  Punching works TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
        
    ##########  Punch Code is required TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
        
    ##########  Punch Codes consist of only numbers TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
        
    ##########  Punch Codes are 5 characters long TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
        
    ##########  Amount of punches is required TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
        
    ##########  Amount should no            " t exceed maximum employee punches allowed TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
        
    ##########  Amount must be greater than 0 TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[8]['test_message'] = str(e)
        
    ##########  Non-existent Punch Code shows approprirate message TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
        
    
    
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
    
    
    ##########  User needs to be logged in to access page TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
        
    ##########  Approving redeem works TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
        
    ##########  Rejecting redeem works TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
        
    ##########  Approved redeem is in the history tab TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
        
    ##########  Rejected redeem is not in the history tab TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
        
    ##########  Approving a redeem when the PatronStore does
    ###         not have enough punches shows error TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
        
    ##########  Approving redeem from a PatronStore that does
    ###         not exist shows error TODO
    try:
        pass 
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
        
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
