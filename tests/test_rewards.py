"""
Selenium tests for dashboard 'My Account' tab.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest
from parse.apps.accounts.models import Account

TEST_USER = {
    "username": "clothing",
    "password": "123456",
    "email": "clothing@vandolf.com",
}

account = Account.objects().get(username=TEST_USER['username'],
    include="Store")
store = account.store
# start with no rewards
store.rewards = []
store.update()

def test_rewards():
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Having no rewards shows a placeholder row"},
        {'test_name': "Adding a reward works"},
        {'test_name': "The new reward is saved to parse"},
        {'test_name': "Updating a reward works"},
        {'test_name': "The updated reward is saved to parse"},
        {'test_name': "The updated reward retains the reward_id"},
        {'test_name': "Deleting a brings up a confirmation dialog"},
        {'test_name': "Deleting a reward works"},
        {'test_name': "The deleted reward is deleted from parse"},
        {'test_name': "Reward name is required"},
        {'test_name': "Punches is required"},
        {'test_name': "Punches must be a number"},
        {'test_name': "Description is not required"},
        {'test_name': "Rewards are initially sorted by Punches " +\
            "from least to greatest"},
        {'test_name': "Punches is sortable"},
        {'test_name': "Name is sortable"},
    ]
    section = {
        "section_name": "Rewards page working properly?",
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
    ##########  Having no rewards shows a placeholder row 
    try:
        parts[1]['success'] =\
            test.find("//div[@id='rewards_section']/div[@class=" +\
            "'tr reward']/div[@class='td reward_summary']/span[1]",
            type="xpath").text == "No Rewards"
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
    ##########  Adding a reward works 
    try:
        test.find
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
    ##########  The new reward is saved to parse TODO
    ##########  Updating a reward works TODO
    ##########  The updated reward is saved to parse TODO
    ##########  The updated reward retains the reward_id TODO
    ##########  Deleting a brings up a confirmation dialog TODO
    ##########  Deleting a reward works TODO
    ##########  The deleted reward is deleted from parse TODO
    ##########  Reward name is required TODO
    ##########  Punches is required TODO
    ##########  Punches must be a number TODO
    ##########  Description is not required TODO
    ##########  Rewards are initially sorted by Punches TODO
    ###         from least to greatest
    ##########  Punches is sortable TODO
    ##########  Name is sortable TODO
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()









