"""
Cloud code function calls for testing to replace the need 
for a physical device.
"""

from parse.utils import cloud_call
from parse.apps.messages.models import Message
from parse.apps.patrons.models import PatronStore
from parse.apps.stores.models import Store

from libs.dateutil.relativedelta import relativedelta

from django.utils import timezone

from random import randint

def request_redeem():
    """
    """
    print _request_redeem("zef0o3YjIm", "o72LmDy0YK", "kfWmOOlIWD",
        "Test Redeem#"+str(randint(0,9999)), 1, 1,
        "Vandolf Estrellado", None, "nSqxOtPMik")
        
def request_redeem_ps(patron_store_id, reward_id=0, num_punches=1):
    ps = PatronStore.objects().get(objectId=patron_store_id,
        include="Patron,Store", order="createdAt")
    print _request_redeem(ps.patron.objectId, ps.store.objectId,
        patron_store_id, "Test Redeem#"+str(randint(0,9999)), reward_id,
        num_punches, "Vandolf Estrellado", None,
        ps.store.store_locations[0].objectId)

def _request_redeem(patron_id, store_id, patron_store_id, title,
    reward_id, num_punches, name, message_status_id, store_location_id):
    """
    var patronId = request.params.patron_id;
	var storeId = request.params.store_id;
	var patronStoreId = request.params.patron_store_id;
	var rewardTitle = request.params.title;
	var rewardId = parseInt(request.params.reward_id);
	var numPunches = parseInt(request.params.num_punches); //comes in as string!
	var customerName = request.params.name;
	var messageStatusId = request.params.message_status_id;
	var isOfferOrGift = (messageStatusId != null);
    """
    return cloud_call("request_redeem", {
        "patron_id": patron_id,
        "store_id": store_id,
        "store_location_id": store_location_id,
        "patron_store_id": patron_store_id,
        "title": title,
        "reward_id": reward_id,
        "num_punches": num_punches,
        "name": name,
        "message_status_id": message_status_id,
    })
    
    
def retailer_message(store_id, message_type):
    rand_str = str(randint(0,9999))
    if message_type == "offer":
        print _retailer_message(store_id, "Test Message #"+rand_str,
            "This is a test message", 
            timezone.now() + relativedelta(years=1),
            message_type, "Offer #"+rand_str, None,
            None, sender_name="Test Store")
    
    elif message_type == "basic":
        pass
    
    elif message_type == "gift":
        pass
    
def _retailer_message(store_id, subject, body, 
    date_offer_expiration, message_type, offer_title, gift_title,
    gift_description, sender_name="Test Store", receiver_count=100,
    is_read=False, filter="all"):
    # first create the message
    message = Message(store_id=store_id, subject=subject, body=body,
        filter=filter, sender_name=sender_name, offer_title=offer_title,
        message_type=message_type, date_offer_expiration=\
        date_offer_expiration, is_read=is_read, gift_description=\
        gift_description, gift_title=gift_title, offer_redeemed=False)
    message.create()
    
    return cloud_call("retailer_message", {
        "subject": subject,
        "message_id": message.objectId,
        "store_id": store_id,
        "store_name": sender_name,
        "filter": filter,
        
    })
    
def request_redeem_offers(patron_store_id):
    """
    Requests all offers in the given patron_store's MessageStatus
    """
    ps = PatronStore.objects().get(objectId=patron_store_id,
        include="Patron,Store")
    patron, store = ps.patron, ps.store
    message_statuses = patron.get("receivedMessages",
        redeem_available="yes", limit=999)

    for ms in message_statuses:
        message = Message.objects().get(objectId=ms.Message)
        cloud_call("request_redeem", {
            "patron_id": ps.Patron,
            "store_id": ps.Store,
            "store_location_id": store.store_locations[0].objectId,
            "patron_store_id": ps.objectId,
            "title": message.offer_title,
            "reward_id": None,
            "num_punches": 0,
            "name": patron.get_fullname(),
            "message_status_id": ms.objectId,
        })
    
def register_employee(first_name, last_name, username, 
    email, password, retailer_pin):
    return cloud_call("register_employee", {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "password": password,
        "email": email,
        "retailer_pin": retailer_pin,
    }) 

def register_rand_employee(store_id):
    name = "Employee" + str(randint(0,9999))
    username = name+"@repunch.com"
    store = Store.objects().get(objectId=store_id, include="Settings")
    
    return register_employee(name, name, username, 
        username, "repunch7575", store.settings.retailer_pin)
        
