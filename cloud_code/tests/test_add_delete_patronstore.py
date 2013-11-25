"""
Tests for add_patronstore and delete_patronstore.
"""

from parse.utils import cloud_call
from cloud_code.tests import CloudCodeTest
from parse.apps.accounts.models import Account
from parse.apps.patrons.models import PatronStore

# This User exists solely for testing CloudCode.
# It must have a Store and Patron pointers.
ACCOUNT_EMAIL = "cloudcode@repunch.com"

def test_add_delete_patronstore():
    """
    This first deletes all the PatronStores that points to this Store.
    """
    print "\ntest_add_delete_patronstore:"
    print "----------------------------"
    
    account = Account.objects().get(email=ACCOUNT_EMAIL,
        include="Patron,Store")
    patron = account.patron
    store = account.store
    
    for ps in PatronStore.objects().filter(Store=store.objectId):
        ps.delete()
    
    test = CloudCodeTest("ADD/DELETE_PATRONSTORE", [
        {'test_name': "Add_patronstore creates a new PatronStore if does not exist"},
        {'test_name': "PatronStore is added to Patron's PatronStores relation"},
        {'test_name': "PatronStore is added to Store's PatronStores relation"},
        {'test_name': "PatronStore's Patron pointer is set"},
        {'test_name': "PatronStore's Store pointer is set"},
        {'test_name': "PatronStore's all_time_punches is set to 0"},
        {'test_name': "PatronStore's punch_count is set to 0"},
        {'test_name': "PatronStore's pending_reward is set to false"},
        
        {'test_name': "Add_patronstore returns existing PatronStore"},
        {'test_name': "PatronStore is in the Patron's PatronStores relation"},
        {'test_name': "PatronStore is in the Store's PatronStores relation"},
        
        {'test_name': "Delete_patronstore deletes the PatronStore"},
        {'test_name': "PatronStore is removed from the Patron's PatronStores relation"},
        {'test_name': "PatronStore is removed from the Store's PatronStores relation"},
    ])
    
    ##########  Add_patronstore creates a new PatronStore if does not exist
    def test_0():
        if PatronStore.objects().count(Patron=patron.objectId,
            Store=store.objectId) == 1:
            return "PatronStore already exists. Test is invalid."
            
        cloud_call("add_patronstore", {
            "patron_id": patron.objectId,
            "store_id": store.objectId,
        })
        
        return PatronStore.objects().count(Patron=patron.objectId,
            Store=store.objectId) == 1
    
    ##########  PatronStore is added to Patron's PatronStores relation
    def test_1():
        patron_store = PatronStore.objects().get(Patron=patron.objectId,
            Store=store.objectId)
        globals()["patron_store"] = patron_store
        return patron.get("patronStores", count=1, limit=0,
            objectId=patron_store.objectId) == 1
    
    ##########  PatronStore is added to Store's PatronStores relation
    def test_2():
        return store.get("patronStores", count=1, limit=0,
            objectId=globals()["patron_store"].objectId) == 1
    
    ##########  PatronStore's Patron pointer is set
    def test_3():
        return globals()["patron_store"].Patron == patron.objectId
    
    ##########  PatronStore's Store pointer is set 
    def test_4():
        return globals()["patron_store"].Store == store.objectId
    
    ##########  PatronStore's all_time_punches is set to 0 
    def test_5():
        return globals()["patron_store"].all_time_punches == 0
    
    ##########  PatronStore's punch_count is set to 0 
    def test_6():
        return globals()["patron_store"].punch_count == 0
    
    ##########  PatronStore's pending_reward is set to false 
    def test_7():
        return not globals()["patron_store"].pending_reward
        
    ##########  Add_patronstore returns existing PatronStore
    def test_8():
        patron_store = globals()["patron_store"]
        if PatronStore.objects().count(\
            objectId=patron_store.objectId) == 0:
            return "PatronStore does not exists. Test is invalid."
            
        cloud_call("add_patronstore", {
            "patron_id": patron.objectId,
            "store_id": store.objectId,
        })
        
        return PatronStore.objects().count(Patron=patron.objectId,
            Store=store.objectId) == 1 and\
            PatronStore.objects().get(Patron=patron.objectId,
            Store=store.objectId).objectId == patron_store.objectId
    
    ##########  PatronStore is in the Patron's PatronStores relation
    def test_9():
        patron_store = PatronStore.objects().get(Patron=patron.objectId,
            Store=store.objectId)
        globals()["patron_store"] = patron_store
        return patron.get("patronStores", count=1, limit=0,
            objectId=patron_store.objectId) == 1
    
    ##########  PatronStore is in the Store's PatronStores relation 
    def test_10():
        return store.get("patronStores", count=1, limit=0,
            objectId=globals()["patron_store"].objectId) == 1
    
    ##########  Delete_patronstore deletes the PatronStore 
    def test_11():
        patron_store = globals()["patron_store"]
        if PatronStore.objects().count(\
            objectId=patron_store.objectId) == 0:
            return "PatronStore does not exists. Test is invalid."
    
        cloud_call("delete_patronstore", {
            "patron_store_id": patron_store.objectId,
            "patron_id": patron.objectId,
            "store_id": store.objectId,
        })
        
        return PatronStore.objects().count(\
            objectId=patron_store.objectId) == 0
    
    ##########  PatronStore is removed from the Patron's PatronStores relation 
    def test_12():
        return patron.get("patronStores", count=1, limit=0,
            objectId=globals()["patron_store"].objectId) == 0
    
    ##########  PatronStore is removed from the Store's PatronStores relation 
    def test_13():
        return store.get("patronStores", count=1, limit=0,
            objectId=globals()["patron_store"].objectId) == 0
    
    for i in range(14):
        test.testit(locals()["test_%s" % (str(i),)])
    
    # END OF ALL TESTS - cleanup
    return test.get_results()
