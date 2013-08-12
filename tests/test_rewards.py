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
        {'test_name': "Redemption count starts at 0"},
        {'test_name': "Reward id starts at 0"},
        {'test_name': "Updating a reward works"},
        {'test_name': "The updated reward is saved to parse"},
        {'test_name': "The updated reward retains the reward_id"},
        {'test_name': "The updated reward retains the " +\
            "redemption_count"},
        {'test_name': "Clicking delete brings up a confirmation " +\
            "dialog"},
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
    test.open(reverse("rewards_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("rewards_index"))
        
    # login
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
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
        
    reward1_name = "Reward #1"
    reward1_description = "First reward"
    reward1_punches = 5
    ##########  Adding a reward works 
    try:
        test.find("#add_reward").click()
        sleep(1)
        selectors = (
            ("#id_reward_name", reward1_name),
            ("#id_description", reward1_description),
            ("#id_punches", str(reward1_punches)),
        )
        test.action_chain(0, selectors, action="send_keys")
        test.find("#submit-reward-form").click()
        sleep(5)
        parts[2]['success'] = test.find("//div[@id=0]/a/div[2]" +\
            "/span[1]", type="xpath").text == reward1_name
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
    ##########  The new reward is saved to parse
    try:
        store.rewards = None
        reward = store.get("rewards")[0]
        parts[3]['success'] = reward['reward_name'] ==\
            reward1_name and reward['description'] ==\
            reward1_description and\
            reward['punches'] == reward1_punches
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
    ##########  Redemption count starts at 0
    try:
        parts[4]['success'] = reward['redemption_count'] == 0
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
    
    ##########  Redemption count starts at 0
    try:
        parts[5]['success'] = reward['reward_id'] == 0
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
        
    # let's add another reward!
    reward2_name = "reward dos"
    reward2_description = "DOS"
    reward2_punches = 10
    test.find("#add_reward").click()
    sleep(1)
    selectors = (
        ("#id_reward_name", reward2_name),
        ("#id_description", reward2_description),
        ("#id_punches", str(reward2_punches)),
    )
    test.action_chain(0, selectors, action="send_keys")
    test.find("#submit-reward-form").click()
    sleep(5)
    
    reward1_name = "reward uno"
    reward1_description = "UNO"
    reward1_punches = 1
    ##########  Updating a reward works
    try:
        test.find("//div[@id=0]/a", type="xpath").click()
        sleep(1)
        selectors = (
            ("#id_reward_name", reward1_name),
            ("#id_description", reward1_description),
            ("#id_punches", str(reward1_punches)),
        )
        test.action_chain(0, selectors, action="clear")
        test.action_chain(0, selectors, action="send_keys")
        test.find("#submit-reward-form").click()
        sleep(5)
        parts[6]['success'] = test.find("//div[@id=0]/a/div[2]" +\
            "/span[1]", type="xpath").text == reward1_name
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
    ##########  The updated reward is saved to parse
    try:
        store.rewards = None
        reward = store.get("rewards")[0] # list is sorted by punches
        parts[7]['success'] = reward['reward_name'] ==\
            reward1_name and\
            reward['description'] == reward1_description and\
            reward['punches'] == reward1_punches
    except Exceptio as e:
        print e
        parts[7]['test_message'] = str(e)
    ##########  The updated reward retains the reward_id 
    try:
        parts[8]['success'] = reward['reward_id'] == 0
    except Exception as e:
        print e
        parts[8]['test_message'] = str(e)
    ##########  The updated reward retains the redemption_count 
    try:
        parts[9]['success'] = reward['redemption_count'] == 0
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
    ##########  Clicking delete brings up a confirmation dialog 
    try:
        test.find("//div[@id='0']/a", type="xpath").click()
        sleep(1)
        test.find("#delete-link").click()
        alert = test.switch_to_alert()
        parts[10]['success'] = alert is not None
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
    ##########  Deleting a reward works
    try:
        alert.accept()
        sleep(5)
        parts[11]['success'] =\
            test.find("//div[@id='rewards_section']/div[@class=" +\
            "'tr reward']/div[@class='td reward_summary']/span[1]",
            type="xpath").text == "No Rewards"
    except Exception as e:
        print e
        parts[11]['test_message'] = str(e)
    ##########  The deleted reward is deleted from parse 
    try:
        store.rewards = None
        rewards = store.get("rewards")
        
    except Exception as e:
        print e
        parts[12]['test_message'] = str(e)
        
        
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









