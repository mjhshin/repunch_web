"""
Cloud code function calls for testing to replace the need 
for a physical device.
"""

from parse.utils import cloud_call

from random import randint

def request_redeem():
    """
    """
    print _request_redeem("DIPSVwKug4", "o72LmDy0YK", "XgGKiDHOQ1",
        "Test Redeem #%s" % (str(randint(0,9999)),), 10, 5, 
        "Vandolf Ex", None)

def _request_redeem(patron_id, store_id, patron_store_id, title,
    reward_id, num_punches, name, message_status_id):
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
        "patron_store_id": patron_store_id,
        "title": title,
        "reward_id": reward_id,
        "num_punches": num_punches,
        "name": name,
        "message_status_id": message_status_id,
    })
