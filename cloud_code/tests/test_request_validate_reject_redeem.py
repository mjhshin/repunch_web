"""
Tests for request, validate, and reject redeem.
"""

from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from cloud_code.tests import CloudCodeTest
from parse.utils import cloud_call
from parse.apps.accounts.models import Account
from parse.apps.patrons.models import PatronStore
from parse.apps.rewards.models import RedeemReward
from parse.apps.messages.models import Message

# This User exists solely for testing CloudCode.
# It must have a Store, Employee, and Patron pointers.
ACCOUNT_EMAIL = "cloudcode@repunch.com"

def test_request_validate_reject_redeem():
    """
    This first deletes all the PatronStores that points to this Store.
    This will also set the Store's rewards, sentMessages, redeemRewards,
    and the Patron's receivedMessages.
    """
    account = Account.objects().get(email=ACCOUNT_EMAIL,
        include="Patron,Store,Employee")
    patron = account.patron
    store = account.store
    employee = account.employee
    
    store.rewards = [{
        "reward_id":0,
        "redemption_count":0,
        "punches":1,
        "reward_name":"ATest Reward",
        "description":"Test Reward",
    }]
    store.update()
    
    reward = store.rewards[0]
    
    if store.get("sentMessages"):
        for m in store.sentMessages:
            m.delete()
        store.sentMessages = None
        
    if store.get("redeemRewards"):
        for r in store.redeemRewards:
            r.delete()
        store.redeemRewards = None
        
    if patron.get("receivedMessages"):
        for ms in patron.receivedMessages:
            ms.delete()
        patron.receivedMessages = None
    
    for ps in PatronStore.objects().filter(Store=store.objectId):
        ps.delete()
    
    patron_store = PatronStore(**cloud_call("add_patronstore", {
        "patron_id": patron.objectId,
        "store_id": store.objectId,
    })["result"])
    
    # first add some punches
    patron_store.all_time_punches = 10
    patron_store.punch_count = 10
    patron_store.update()
    
    test = CloudCodeTest("REQUEST/APPROVE/REJECT REDEEM", [
        {'test_name': "Request_redeem creates a new RedeemReward (reward)"},
        {'test_name': "RedeemReward is added to Store's RedeemReward relation"},
        {'test_name': "PatronStore's pending_reward is set to true"},
        {'test_name': "RedeemReward's patron_id is set"},
        {'test_name': "RedeemReward's customer_name is set"},
        {'test_name': "RedeemReward's is_redeemed is set to false"},
        {'test_name': "RedeemReward's title is set"},
        {'test_name': "RedeemReward's PatronStore pointer is set"},
        {'test_name': "RedeemReward's num_punches is set"},
        {'test_name': "RedeemReward's reward_id is set"},
        
        {'test_name': "Validate_redeem successful"},
        {'test_name': "RedeemReward's is_redeemed is set to true"},
        {'test_name': "PatronStore's pending_reward is set to false"},
        {'test_name': "PatronStore's punch_count is updated"},
        {'test_name': "The reward's redemption_count is updated"},
        
        {'test_name': "Reject_redeem successful"},
        {'test_name': "RedeemReward is deleted"},
        {'test_name': "PatronStore's pending_reward is set to false"},
        
        {'test_name': "Request_redeem creates a new RedeemReward (offer/gift)"},
        {'test_name': "RedeemReward is added to Store's RedeemReward relation"},
        {'test_name': "RedeemReward's num_punches is set to 0 regardless of input"},
        {'test_name': "RedeemReward's MessageStatus is set"},
        {'test_name': "RedeemReward's patron_id is set"},
        {'test_name': "RedeemReward's customer_name is set"},
        {'test_name': "RedeemReward's is_redeemed is set to false"},
        {'test_name': "RedeemReward's title is set"},
        {'test_name': "MessageStatus' redeem_available is set to pending"},
        
        {'test_name': "Validate_redeem successful"},
        {'test_name': "RedeemReward's is_redeemed is set to true"},
        {'test_name': "MessageStatus's redeem_available is set to 'no'"},
        
        {'test_name': "Reject_redeem successful"},
        {'test_name': "RedeemReward is deleted"},
        {'test_name': "MessageStatus's redeem_available is set to 'no'"},
        
        {'test_name': "Request_redeem succeeds with pending if"+\
            " PatronStore's pending_reward is true before the request."},
            
        {'test_name': "Validate_redeem succeeds with validated if the"+\
            "RedeemReward has already been redeemed"},
        {'test_name': "Validate_redeem succeeds with PATRONSTORE_REMOVED if the"+\
            "PatronStore has been deleted"},
        {'test_name': "The RedeemReward is then deleted."},
            
        {'test_name': "Validate_redeem succeeds with insufficient if the"+\
            "PatronStore does not have enough punches"},
        {'test_name': "The RedeemReward is then deleted."},
        {'test_name': "Validate_redeem fails with REDEEMREWARD_NOT_FOUND if the"+\
            "RedeemReward has been deleted"},
            
        {'test_name': "Reject_redeem fails with REDEEMREWARD_VALIDATED"+\
            "if the RedeemReward has already been validated"},
        {'test_name': "Reject_redeem fails with REDEEMREWARD_NOT_FOUND if the"+\
            "RedeemReward has been deleted"},
        {'test_name': "Reject_redeem fails with PATRONSTORE_REMOVED if the"+\
            "PatronStore has been deleted"},
        {'test_name': "The RedeemReward is then deleted."},
    ])
    
    def request_redeem(reward_id=reward["reward_id"],
        title=reward["reward_name"], message_status_id=None):
        return cloud_call("request_redeem", {
            "patron_id": patron.objectId,
            "store_id": store.objectId,
            "patron_store_id": patron_store.objectId,
            "reward_id": reward_id,
            "num_punches": reward["punches"],
            "name": patron.get_fullname(),
            "title": title,
            "message_status_id": message_status_id,
        })
    
    ##########  Request_redeem creates a new RedeemReward (reward)
    def test_0():
        if RedeemReward.objects().count(\
            PatronStore=patron_store.objectId) > 0:
            return "PatronStore exists. Test is invalid."
        
        request_redeem()
        
        return RedeemReward.objects().count(\
            PatronStore=patron_store.objectId) == 1
    
    test.testit(test_0)
    
    redeem_reward = RedeemReward.objects().get(\
            PatronStore=patron_store.objectId)
    patron_store.fetch_all(clear_first=True, with_cache=False)
    
    ##########  RedeemReward is added to Store's RedeemReward relation
    def test_1():
        return store.get("redeemRewards", objectId=redeem_reward.objectId,
            count=1, limit=0) == 1
    
    test.testit(test_1)
    
    ##########  PatronStore's pending_reward is set to true
    def test_2():
        return patron_store.pending_reward
    
    test.testit(test_2)
    
    ##########  RedeemReward's patron_id is set 
    def test_3():
        return redeem_reward.patron_id == patron.objectId
    
    test.testit(test_3)
    
    ##########  RedeemReward's customer_name is set
    def test_4():
        return redeem_reward.customer_name == patron.get_fullname()
    
    test.testit(test_4)
    
    ##########  RedeemReward's is_redeemed is set to false
    def test_5():
        return not redeem_reward.is_redeemed
    
    test.testit(test_5)
    
    ##########  RedeemReward's title is set
    def test_6():
        return redeem_reward.title == reward["reward_name"]
    
    test.testit(test_6)
    
    ##########  RedeemReward's PatronStore pointer is set 
    def test_7():
        return redeem_reward.PatronStore == patron_store.objectId
    
    test.testit(test_7)
    
    ##########  RedeemReward's num_punches is set 
    def test_8():
        return redeem_reward.num_punches == reward["punches"]
    
    test.testit(test_8)
    
    ##########  RedeemReward's reward_id is set 
    def test_9():
        return redeem_reward.reward_id == reward["reward_id"]
    
    test.testit(test_9)
    
    pt_punch_cout_b4 = patron_store.punch_count
    reward_red_count_b4 = reward["redemption_count"]
        
    ##########  Validate_redeem successful
    def test_10():
        res = cloud_call("validate_redeem", {
            "redeem_id": redeem_reward.objectId,
            "store_id": store.objectId,
            "reward_id": reward["reward_id"],
        })
        
        return "error" not in res
    
    test.testit(test_10)
    
    redeem_reward.fetch_all(clear_first=True, with_cache=False)
    patron_store.fetch_all(clear_first=True, with_cache=False)
    store.rewards = None
    reward = store.get("rewards")[0]
    
    ##########  RedeemReward's is_redeemed is set to true
    def test_11():
        return redeem_reward.is_redeemed
    
    test.testit(test_11)
    
    ##########  PatronStore's pending_reward is set to false
    def test_12():
        return not patron_store.pending_reward
    
    test.testit(test_12)
    
    ##########  PatronStore's punch_count is updated 
    def test_13():
        return patron_store.punch_count ==\
            pt_punch_cout_b4 - reward["punches"]
    
    test.testit(test_13)
    
    ##########  The reward's redemption_count is updated 
    def test_14():
        return reward["redemption_count"] ==\
            reward_red_count_b4 + 1
        
    test.testit(test_14)
    
    # need a new redeem
    request_redeem()
    redeem_reward = RedeemReward.objects().get(\
            PatronStore=patron_store.objectId, is_redeemed=False)
    
    ##########  Reject_redeem successful
    def test_15():
        res = cloud_call("reject_redeem", {
            "redeem_id": redeem_reward.objectId,
            "store_id": store.objectId,
        })
        
        return "error" not in res
    
    test.testit(test_15)
    
    patron_store.fetch_all(clear_first=True, with_cache=False)
    
    ##########  RedeemReward is deleted
    def test_16():
        return RedeemReward.objects().count(\
            objectId=redeem_reward.objectId) == 0
    
    test.testit(test_16)
    
    ##########  PatronStore's pending_reward is set to false
    def test_17():
        return not patron_store.pending_reward
    
    test.testit(test_17)
    
    # need to create an offer
    def create_offer():
        offer = Message.objects().create(**{
            'subject': u'test_request_validate_redeem script message offer',
            'body': u'test_request_validate_redeem script generate offer', 
            'sender_name': u'test_request_validate_redeem', 
            'store_id': store.objectId, 
            'is_read': False, 
            'offer_redeemed': False, 
            'date_offer_expiration': timezone.now()+relativedelta(days=1), 
            'filter': u'all', 
            'offer_title': u'test_request_validate_redeem script offer', 
            'message_type': 'offer', 
        })
        
        cloud_call("retailer_message", {
            "filter": offer.filter,
            "store_name": store.store_name,
            "message_id": offer.objectId,
            "store_id": store.objectId,
            "subject": offer.subject,
        })
        
        return offer
    
    offer = create_offer()
    message_status = patron.get("receivedMessages", limit=1)[0]
    patron.receivedMessages = None
        
    ##########  Request_redeem creates a new RedeemReward (offer/gift)
    def test_18():
        request_redeem(None, offer.offer_title, message_status.objectId)
        
        return RedeemReward.objects().count(\
            MessageStatus=message_status.objectId,
            is_redeemed=False) == 1
    
    test.testit(test_18)
    
    redeem_reward = RedeemReward.objects().get(\
            MessageStatus=message_status.objectId, is_redeemed=False)
            
    ##########  RedeemReward is added to Store's RedeemReward relation
    def test_19():
        store.redeemRewards = None
        return store.get("redeemRewards", objectId=\
            redeem_reward.objectId, count=1, limit=0) == 1
        
    test.testit(test_19)
    
    ##########  RedeemReward's num_punches is set to 0 regardless of input
    def test_20():
        return redeem_reward.num_punches == 0
    
    test.testit(test_20)
    
    ##########  RedeemReward's MessageStatus is set
    def test_21():
        return redeem_reward.MessageStatus == message_status.objectId
    
    test.testit(test_21)
    
    ##########  RedeemReward's patron_id is set
    def test_22():
        return redeem_reward.patron_id == patron.objectId
    
    test.testit(test_22)
    
    ##########  RedeemReward's customer_name is set
    def test_23():
        return redeem_reward.customer_name == patron.get_fullname()
    
    test.testit(test_23)
    
    ##########  RedeemReward's is_redeemed is set to false
    def test_24():
        return not redeem_reward.is_redeemed
    
    test.testit(test_24)
    
    ##########  RedeemReward's title is set
    def test_25():
        return redeem_reward.title == offer.offer_title
    
    test.testit(test_25)
    
    ##########  MessageStatus' redeem_available is set to pending
    def test_26():
        message_status.redeem_available = None
        return message_status.get("redeem_available") == "pending"
    
    test.testit(test_26)
        
    ##########  Validate_redeem successful
    def test_27():
        res = cloud_call("validate_redeem", {
            "redeem_id": redeem_reward.objectId,
            "store_id": store.objectId,
        })
        
        return "error" not in res
    
    test.testit(test_27)
    
    redeem_reward.fetch_all(clear_first=True, with_cache=False)
    message_status.fetch_all(clear_first=True, with_cache=False)
    
    ##########  RedeemReward's is_redeemed is set to true
    def test_28():
        return redeem_reward.is_redeemed
    
    test.testit(test_28)
    
    ##########  MessageStatus's redeem_available is set to "no"
    def test_29():
        return message_status.redeem_available == "no"
    
    test.testit(test_29)
    
    # create another redeem
    offer = create_offer()
    message_status = patron.get("receivedMessages",
        redeem_available="yes", limit=1)[0]
    patron.receivedMessages = None
    request_redeem(None, offer.offer_title, message_status.objectId)
    redeem_reward = RedeemReward.objects().get(\
            MessageStatus=message_status.objectId, is_redeemed=False)
            
    ##########  Reject_redeem successful
    def test_30():
        res = cloud_call("reject_redeem", {
            "redeem_id": redeem_reward.objectId,
            "store_id": store.objectId,
        })
        return "error" not in res
    
    test.testit(test_30)
    
    ##########  RedeemReward is deleted
    def test_31():
        return  RedeemReward.objects().count(\
            objectId=redeem_reward.objectId) == 0
    
    test.testit(test_31)
    
    ##########  MessageStatus' redeem_available is set to "no"
    def test_32():
        message_status.redeem_available = None
        return message_status.get("redeem_available") == "no"
    
    test.testit(test_32)
        
    ##########  Request_redeem succeeds with pending if
    ###         PatronStore's pending_reward is true before the request.
    def test_33():
        patron_store.pending_reward = True
        patron_store.update()
        res = request_redeem()
        return res["result"] == "pending"
    
    test.testit(test_33)
            
    ##########  Validate_redeem succeeds with validated if the
    ###         RedeemReward has already been redeemed TODO
    
    ##########  Validate_redeem succeeds with PATRONSTORE_REMOVED if the
    ###         PatronStore has been deleted TODO
    ##########  The RedeemReward is then deleted TODO
        
    ##########  Validate_redeem succeeds with insufficient if the
    ###         PatronStore does not have neough punches TODO
    ##########  The RedeemReward is then deleted TODO
        
    ##########  Validate_redeem fails with REDEEMREWARD_NOT_FOUND if the
    ###         RedeemReward has been deleted TODO
            
    ##########  Reject_redeem fails with REDEEMREWARD_VALIDATED
    ###         if the RedeemReward has already been validated TODO
    
    ##########  Reject_redeem fails with REDEEMREWARD_NOT_FOUND if the
    ###         RedeemReward has been deleted TODO
    
    ##########  Reject_redeem fails with PATRONSTORE_REMOVED if the
    ###         PatronStore has been deleted TODO
    ##########  The RedeemReward is then deleted TODO
    
    
    # END OF ALL TESTS - cleanup
    return test.get_results()
