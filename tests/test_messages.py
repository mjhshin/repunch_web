"""
Selenium tests for dashboard 'Messages' tab.
"""

from django.core.urlresolvers import reverse
from django.utils import timezone
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
    include="Store.Subscription")
store = account.store
subscription = store.subscription

# set subscriptionType to middle
subscription.subscriptionType = 1
subscription.update()

# clear the sent messages relation
sent_messages = store.get("sentMessages", keys="")
if sent_messages:
    store.remove_relation("SentMessages_",
        [m.objectId for m in sent_messages])
# clear the received messages relation
received_messages = store.get("receivedMessages", keys="")
if received_messages:
    store.remove_relation("ReceivedMessages_",
        [m.objectId for m in received_messages])
        
# we can clear the list locally but just re-pull from parse
account = Account.objects().get(username=TEST_USER['username'],
    include="Store")
store = account.store

def test_messages():
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        
        {'test_name': "Send message. Filter all. No offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        
        {'test_name': "Send message. Filter all. With offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        
        {'test_name': "Message limit passed (free) dialog appears"},
        {'test_name': "Upgrading account from the dialog sends the " +\
            "message and upgrades the account to middle"},
        {'test_name': "Email is sent notifying user the upgrade"},
            
        {'test_name': "Send message. Filter idle. No offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        
        {'test_name': "Send message. Filter idle. With offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        
        {'test_name': "Message limit passed (middle) dialog appears"},
        {'test_name': "Upgrading account from the dialog sends the" +\
            " message and upgrades the account to heavy"},
        {'test_name': "Email is sent notifying user the upgrade"},
            
        {'test_name': "Send message. Filter loyal. No offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        
        {'test_name': "Send message. Filter loyal. With offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        
        {'test_name': "Send message. Filter all. With offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        
        {'test_name': "Send message. Filter all. With offer"},
        
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        
        {'test_name': "Message limit passed (heavy) dialog appears"},
        {'test_name': "Account can no longer be upgraded." +\
            "Message cannot be sent"},
            
        {'test_name': "Subject is required"},
        {'test_name': "Body is required"},
        {'test_name': "Offer title not required if attach offer off"},
        {'test_name': "Expiration not required if attach offer off"},
        {'test_name': "Offer title is required if attach offer on"},
        {'test_name': "Expiration date required if attach offer on"},
        {'test_name': "Expiration date must be at a later date"},
        {'test_name': "Expiration date must be at most 1 year later"},
        
        {'test_name': "Clicking cancel prompts the user in deletion"},
        {'test_name': "Canceling redirects user back to messages" +\
            "index"},
            
    ]
    section = {
        "section_name": "Messages page working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("messages_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("messages_index"))
        
    # login
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(7) 
    
    
    ##########  User needs to be logged in to access page. 
        
    ##########  Send message. Filter all. No offer. 
    ##########  Message is in store's sentMessages relation. 
    ##########  Message is visible in page. 
    ##########  Message can be view by clicking on row. 

    ##########  Send message. Filter all. With offer. 
    ##########  Message is in store's sentMessages relation. 
    ##########  Message is visible in page. 
    ##########  Message can be view by clicking on row. 

    ##########  Message limit passed (free) dialog appears. 
    ##########  Upgrading account from the dialog sends the 
    ###         message and upgrades the account to middle. 
    ##########  Email is sent notifying user the upgrade. 
        
    ##########  Send message. Filter idle. No offer. 
    ##########  Message is in store's sentMessages relation. 
    ##########  Message is visible in page. 
    ##########  Message can be view by clicking on row. 

    ##########  Send message. Filter idle. With offer. 
    ##########  Message is in store's sentMessages relation. 
    ##########  Message is visible in page. 
    ##########  Message can be view by clicking on row. 

    ##########  Message limit passed (middle) dialog appears. 
    ##########  Upgrading account from the dialog sends the
    ###         message and upgrades the account to heavy. 
    ##########  Email is sent notifying user the upgrade. 
        
    ##########  Send message. Filter loyal. No offer. 
    ##########  Message is in store's sentMessages relation. 
    ##########  Message is visible in page. 
    ##########  Message can be view by clicking on row. 

    ##########  Send message. Filter loyal. With offer. 
    ##########  Message is in store's sentMessages relation. 
    ##########  Message is visible in page. 
    ##########  Message can be view by clicking on row. 

    ##########  Send message. Filter all. With offer. 
    ##########  Message is in store's sentMessages relation. 
    ##########  Message is visible in page. 
    ##########  Message can be view by clicking on row. 

    ##########  Send message. Filter all. With offer. 

    ##########  Message is in store's sentMessages relation. 
    ##########  Message is visible in page. 
    ##########  Message can be view by clicking on row. 

    ##########  Message limit passed (heavy) dialog appears. 
    ##########  Account can no longer be upgraded
    ###         Message cannot be sent. 
        
    ##########  Subject is required. 
    ##########  Body is required. 
    ##########  Offer title not required if attach offer off. 
    ##########  Expiration not required if attach offer off. 
    ##########  Offer title is required if attach offer on. 
    ##########  Expiration date required if attach offer on. 
    ##########  Expiration date must be at a later date. 
    ##########  Expiration date must be at most 1 year later. 

    ##########  Clicking cancel prompts the user in deletion. 
    ##########  Canceling redirects user back to messages index. 
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
    
    
def test_feedback():
    pass
    
    
    
    
    
    
    
    
    
