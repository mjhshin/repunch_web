"""
Tests for request, validate, and reject redeem.
"""

from parse.utils import cloud_call
from cloud_code.tests import CloudCodeTest
from parse.apps.accounts.models import Account
from parse.apps.patrons.models import PatronStore

# This User exists solely for testing CloudCode.
# It must have a Store, Employee, and Patron pointers.
ACCOUNT_EMAIL = "cloudcode@repunch.com"

def test_request_validate_reject_redeem():
    """
    This first deletes all the PatronStores that points to this Store.
    """
    account = Account.objects().get(email=ACCOUNT_EMAIL,
        include="Patron,Store,Employee")
    patron = account.patron
    store = account.store
    employee = account.employee
    
    for ps in PatronStore.objects().filter(Store=store.objectId):
        ps.delete()
    
    patron_store = PatronStore(**cloud_call("add_patronstore", {
        "patron_id": patron.objectId,
        "store_id": store.objectId,
    })["result"])
    
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
        {'test_name': "PatronStore's punch_Count is updated"},
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
    
        ##########  Request_redeem creates a new RedeemReward (reward) TODO
    ##########  RedeemReward is added to Store's RedeemReward relation TODO
    ##########  PatronStore's pending_reward is set to true TODO
    ##########  RedeemReward's patron_id is set TODO
    ##########  RedeemReward's customer_name is set TODO
    ##########  RedeemReward's is_redeemed is set to false TODO
    ##########  RedeemReward's title is set TODO
    ##########  RedeemReward's PatronStore pointer is set TODO
    ##########  RedeemReward's num_punches is set TODO
    ##########  RedeemReward's reward_id is set TODO
        
    ##########  Validate_redeem successful TODO
    ##########  RedeemReward's is_redeemed is set to true TODO
    ##########  PatronStore's pending_reward is set to false TODO
    ##########  PatronStore's punch_Count is updated TODO
    ##########  The reward's redemption_count is updated TODO
        
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
