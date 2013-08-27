"""
Selenium tests for dashboard 'Rewards' tab.
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

def test_rewards():
    # setup
    account = Account.objects().get(username=TEST_USER['username'],
        include="Store")
    store = account.store
    # start with no rewards
    store.rewards = []
    store.update()
    
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
        {'test_name': "Description is not required"},
        {'test_name': "Clicking cancel redirects user " +\
            "back to rewards index"},
        {'test_name': "Punches must be a number"},
        {'test_name': "Punches must be greater than 0"},
        {'test_name': "Rewards are initially sorted by Punches " +\
            "from least to greatest"},
        {'test_name': "Punches is sortable"},
        {'test_name': "Name is sortable"},
        {'test_name': "Updating a reward with the reset redemption" +\
            " count option resets the redemption count to 0"},
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
        
    def add_reward(name, description, punches):
        test.find("#add_reward").click()
        sleep(1)
        selectors = (
            ("#id_reward_name", name),
            ("#id_description", description),
            ("#id_punches", str(punches)),
        )
        test.action_chain(0, selectors, action="send_keys")
        test.find("#submit-reward-form").click()
        sleep(5)
        
    reward1_name = "Reward #1"
    reward1_description = "First reward"
    reward1_punches = 5
    ##########  Adding a reward works 
    try:
        add_reward(reward1_name, reward1_description, reward1_punches)
        parts[2]['success'] = test.find("//div[@id='0']/a/div[2]" +\
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
        
    # let's add 3 more rewards!
    reward2_name = "reward dos"
    reward2_description = "DOS"
    reward2_punches = 10
    reward3_name = "reward tres"
    reward3_description = "TRES"
    reward3_punches = 12
    test.find("#add_reward").click()
    reward4_name = "reward quatro"
    reward4_description = "QUATRO"
    reward4_punches = 15
    
    add_reward(reward2_name, reward2_description, reward2_punches)
    add_reward(reward3_name, reward3_description, reward3_punches)
    add_reward(reward4_name, reward4_description, reward4_punches)
    ################
    
    reward1_name = "reward uno"
    reward1_description = "UNO"
    reward1_punches = 1
    ##########  Updating a reward works
    try:
        test.find("//div[@id='0']/a", type="xpath").click()
        sleep(1)
        selectors = (
            ("#id_reward_name", reward1_name),
            ("#id_description", reward1_description),
            ("#id_punches", str(reward1_punches)),
        )
        test.action_chain(0, selectors, action="clear")
        test.action_chain(0, selectors, action="send_keys")
        test.find("#submit-reward-form").click()
        sleep(4)
        parts[6]['success'] = test.find("//div[@id='0']/a/div[2]" +\
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
    except Exception as e:
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
        parts[11]['success'] = test.find("//div[@id='1']/a/div[2]" +\
            "/span[1]", type="xpath").text == reward2_name
        try: # first reward should be gone
            test.find("//div[@id='0']/a/div[2]" +\
                "/span[1]", type="xpath").text
        except Exception:
            parts[11]['success'] = parts[11]['success']
        else:
            parts[11]['success'] = False
    except Exception as e:
        print e
        parts[11]['test_message'] = str(e)
    ##########  The deleted reward is deleted from parse 
    try:
        store.rewards = None
        rewards = store.get("rewards")
        parts[12]['success'] = reward1_name not in\
            [r['reward_name'] for r in rewards] and\
            0 not in [r['reward_id'] for r in rewards]
    except Exception as e:
        print e
        parts[12]['test_message'] = str(e)
        
    # field required
    add_reward("   ", "", "")
        
    ##########  Reward name is required
    try:
        parts[13]['success'] =\
            test.find("#reward_name_ic ul li").text ==\
                "This field is required."
    except Exception as e:
        print e
        parts[13]['test_message'] = str(e)
    ##########  Punches is required
    try:
        parts[14]['success'] =\
            test.find("#punches_ic ul li").text ==\
                "This field is required."
    except Exception as e:
        print e
        parts[14]['test_message'] = str(e)
    ##########  Description is not required 
    try:
        parts[15]['success'] =\
            not test.element_exists("#description_ic ul li")
    except Exception as e:
        print e
        parts[15]['test_message'] = str(e)
    ##########  Clicking cancel redirects user back to rewards index
    try:
        test.find("//div [@id='edit-reward-options']/a[2]", 
            type="xpath").click()
        sleep(2)
        parts[16]['success'] =\
            test.is_current_url(reverse("rewards_index"))
    except Exception as e:
        print e
        parts[16]['test_message'] = str(e)
    ##########  Punches must be a number
    try:
        add_reward("", "", "ba")
        parts[17]['success'] =\
            test.find("#punches_ic ul li").text ==\
                "Enter a whole number."
        test.find("//div [@id='edit-reward-options']/a[2]", 
            type="xpath").click()
        sleep(2)
    except Exception as e:
        print e
        parts[17]['test_message'] = str(e)
        
    ##########  Punches must be greater than 0 
    try:
        add_reward("", "", "0")
        parts[18]['success'] =\
            test.find("#punches_ic ul li").text ==\
                "Ensure this value is greater than or equal to 1."
        test.find("//div [@id='edit-reward-options']/a[2]", 
            type="xpath").click()
        sleep(2)
    except Exception as e:
        print e
        parts[18]['test_message'] = str(e)
    
    
    ##########  Rewards are initially sorted by Punchess
    ###         from least to greatest
    try:
        store.rewards = None
        rewards = store.get('rewards')
        punches_map = {r['punches']:r for r in rewards}
        ascending = [r['punches'] for r in rewards]
        descending = ascending[:]
        ascending.sort()
        descending.sort(reverse=True)
        success = True
        for i in range(3):
            if int(test.find("//div[@id='%s']/a/div[1]" %(str(i+1),),
                type="xpath").text) != ascending[i]:
                success = False
                break
                
        parts[19]['success'] = success
    except Exception as e:
        print e
        parts[19]['test_message'] = str(e)
    ##########  Punches is sortable
    try:
        test.find("#header-reward_punches").click()
        rows = test.find("//div[@id='rewards_section']/" +\
            "div[contains(@class, 'reward')]",
            type="xpath", multiple=True)
            
        if len(rows) == len(descending):
            success = True
            for i in range(len(rows)):
                # check both the punches and id
                row = rows[i]
                if int(row.text.split("\n")[0]) !=\
                    descending[i] or int(row.get_attribute("id")) !=\
                    punches_map[descending[i]]['reward_id']:
                    success = False
                    break
                    
            parts[20]['success'] = success
            
    except Exception as e:
        print e
        parts[20]['test_message'] = str(e)
    ##########  Name is sortable
    try:
        name_map = {r['reward_name']:r for r in rewards}
        ascending = [r['reward_name'] for r in rewards]
        descending = ascending[:]
        ascending.sort()
        descending.sort(reverse=True)
        
        # ascending order
        test.find("#header-reward_summary").click()
        rows = test.find("//div[@id='rewards_section']/" +\
            "div[contains(@class, 'reward')]",
            type="xpath", multiple=True)
            
        if len(rows) == len(ascending):
            success1 = True
            for i in range(len(rows)):
                # check both the name and id
                row = rows[i]
                if row.text.split("\n")[1] !=\
                    ascending[i] or int(row.get_attribute("id")) !=\
                    name_map[ascending[i]]['reward_id']:
                    success1 = False
                    break
                    
        # descending order
        test.find("#header-reward_summary").click()
        rows = test.find("//div[@id='rewards_section']/" +\
            "div[contains(@class, 'reward')]",
            type="xpath", multiple=True)
            
        if len(rows) == len(descending):
            success2 = True
            for i in range(len(rows)):
                # check both the name and id
                row = rows[i]
                if row.text.split("\n")[1] !=\
                    descending[i] or int(row.get_attribute("id")) !=\
                    name_map[descending[i]]['reward_id']:
                    success2 = False
                    break
                    
            parts[21]['success'] = success1 and success2
    except Exception as e:
        print e
        parts[21]['test_message'] = str(e)
        
    ##########  Updating a reward with the reset redemption
    ###         count option resets the redemption count to 0 TODO
    try:
        # logout
        test.find("#link-logout").click()
        sleep(1)
        # modify store the rewards redemption count
        store.rewards = None
        for r in store.get("rewards"):
            r['redemption_count'] = 99
        store.update()
        # login
        test.open(reverse("rewards_index")) # ACTION!
        sleep(1)
        selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
        )
        test.action_chain(0, selectors, "send_keys") # ACTION!
        sleep(7)
        # now test
        test.find("//div[@id='2']/a", type="xpath").click()
        sleep(1)
        red_count = int(test.find("#redemption_count").split(" ")[1])
        test.find("#reset_red_count").click()
        test.find("#submit-reward-form").click()
        sleep(5)
        test.find("//div[@id='2']/a", type="xpath").click()
        new_red_count =\
            int(test.find("#redemption_count").split(" ")[1])
        parts[22]['success'] = new_red_count == 0 and red_count !=\
            new_red_count
    except Exception as e:
        print e
        parts[22]['test_message'] = str(e)
        
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()



