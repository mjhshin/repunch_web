"""
Tests for request, validate, and reject redeem.
"""

from parse.utils import cloud_call
from cloud_code.tests import CloudCodeTest
from parse.apps.accounts.models import Account
from parse.apps.patrons.models import PatronStore
from parse.apps.rewards.models import RedeemReward

# This User exists solely for testing CloudCode.
# It must have a Store, Employee, and Patron pointers.
ACCOUNT_EMAIL = "cloudcode@repunch.com"

def test_request_validate_reject_redeem():
    """
    This first deletes all the PatronStores that points to this Store.
    This will also set the Store's rewards.
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
        
        {'test_name': "Reject_redeem successful"},
        {'test_name': "RedeemReward is deleted"},
        
        {'test_name': "Request_redeem succeeds with pending if"+\
            " PatronStore's pending_reward is true before the request."},
            
        {'test_name': "Validate_redeem succeeds with validated if the"+\
            "RedeemReward has already been redeemed"},
        {'test_name': "Validate_redeem succeeds with PATRONSTORE_REMOVED if the"+\
            "PatronStore has been deleted"},
        {'test_name': "Validate_redeem succeeds with insufficient if the"+\
            "PatronStore does not have neough punches"},
        {'test_name': "Validate_redeem fails with REDEEMREWARD_NOT_FOUND if the"+\
            "RedeemReward has been deleted"},
            
        {'test_name': "Reject_redeem fails with REDEEMREWARD_VALIDATED"+\
            "if the RedeemReward has already been validated"},
        {'test_name': "Reject_redeem fails with REDEEMREWARD_NOT_FOUND if the"+\
            "RedeemReward has been deleted"},
        {'test_name': "Reject_redeem fails with PATRONSTORE_REMOVED if the"+\
            "PatronStore has been deleted"},
    ])
    
    ##########  Request_redeem creates a new RedeemReward (reward)
    def test_0():
        if RedeemReward.objects().count(\
            PatronStore=patron_store.objectId) > 0:
            return "PatronStore exists. Test is invalid."
        
        cloud_call("request_redeem", {
            "patron_id": patron.objectId,
            "store_id": store.objectId,
            "patron_store_id": patron_store.objectId,
            "reward_id": reward["reward_id"],
            "num_punches": reward["punches"],
            "name": patron.get_fullname(),
            "title": reward["reward_name"]
        })
        
        return RedeemReward.objects().count(\
            PatronStore=patron_store.objectId) == 1
    
    test.testit(test_0)
    
    redeem_reward = RedeemReward.objects().get(\
            PatronStore=patron_store.objectId)
    
    ##########  RedeemReward is added to Store's RedeemReward relation
    def test_1():
        return store.get("redeemRewards", objectId=redeem_reward.objectId,
            count=1, limit=0) == 1
    
    test.testit(test_1)
    
    patron_store.fetch_all(clear_first=True, with_cache=False)
    
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
        
    ##########  Reject_redeem successful TODO
    ##########  RedeemReward is deleted TODO
    ##########  PatronStore's pending_reward is set to false TODO
        
    ##########  Request_redeem creates a new RedeemReward (offer/gift) TODO
    ##########  RedeemReward is added to Store's RedeemReward relation TODO
    ##########  RedeemReward's num_punches is set to 0 regardless of input TODO
    ##########  RedeemReward's MessageStatus is set TODO
    ##########  RedeemReward's patron_id is set TODO
    ##########  RedeemReward's customer_name is set TODO
    ##########  RedeemReward's is_redeemed is set to false TODO
    ##########  RedeemReward's title is set TODO
    ##########  MessageStatus' redeem_available is set to pending TODO
        
    ##########  Validate_redeem successful TODO
    ##########  RedeemReward's is_redeemed is set to true TODO
        
    ##########  Reject_redeem successful TODO
    ##########  RedeemReward is deleted TODO
        
    ##########  Request_redeem succeeds with pending if
    ###         PatronStore's pending_reward is true before the request. TODO
            
    ##########  Validate_redeem succeeds with validated if the
    ###         RedeemReward has already been redeemed TODO
    ##########  Validate_redeem succeeds with PATRONSTORE_REMOVED if the
    ###         PatronStore has been deleted TODO
    ##########  Validate_redeem succeeds with insufficient if the
    ###         PatronStore does not have neough punches TODO
    ##########  Validate_redeem fails with REDEEMREWARD_NOT_FOUND if the
    ###         RedeemReward has been deleted TODO
            
    ##########  Reject_redeem fails with REDEEMREWARD_VALIDATED
    ###         if the RedeemReward has already been validated TODO
    ##########  Reject_redeem fails with REDEEMREWARD_NOT_FOUND if the
    ###         RedeemReward has been deleted TODO
    ##########  Reject_redeem fails with PATRONSTORE_REMOVED if the
    ###         PatronStore has been deleted TODO
    
    
    # END OF ALL TESTS - cleanup
    return test.get_results()
