"""
Tests for punch.
"""

from parse.utils import cloud_call
from cloud_code.tests import CloudCodeTest
from parse.apps.accounts.models import Account
from parse.apps.rewards.models import Punch
from parse.apps.patrons.models import PatronStore

# This User exists solely for testing CloudCode.
# It must have a Store, Employee, and Patron pointers.
ACCOUNT_EMAIL = "cloudcode@repunch.com"

def test_punch():
    """
    This first deletes all the PatronStores that points to this Store.
    All Punch objects for the Account's Patron are deleted.
    """
    print "\ntest_punch:"
    print "-----------"
    
    account = Account.objects().get(email=ACCOUNT_EMAIL,
        include="Patron,Store,Employee")
    patron = account.patron
    store = account.store
    employee = account.employee
    
    for ps in PatronStore.objects().filter(Store=store.objectId):
        ps.delete()
    
    for punch in Punch.objects().filter(Patron=patron.objectId):
        punch.delete()
    
    test = CloudCodeTest("PUNCH", [
        {'test_name': "Punch creates a new Punch object (from employee)"},
        {'test_name': "Punch object is added to Store's Punches relation"},
        {'test_name': "Punch object is added to Employee's Punches relation"},
        {'test_name': "Punch's Patron pointer is set"},
        {'test_name': "Punch's  punches is set to correct amount"},
        {'test_name': "Employee's lifetime_punches is updated"},
        {'test_name': "PatronStore is created since it does not yet exist"},
        {'test_name': "PatronStore is added to Patron's PatronStores relation"},
        {'test_name': "PatronStore is added to Store's PatronStores relation"},
        {'test_name': "PatronStore's Patron pointer is set"},
        {'test_name': "PatronStore's Store pointer is set"},
        {'test_name': "PatronStore's all_time_punches is set to amount given"},
        {'test_name': "PatronStore's punch_count is set to amount given"},
        {'test_name': "PatronStore's pending_reward is set to false"},
        
        {'test_name': "Punch creates a new Punch object (from dashboard - owner)"},
        {'test_name': "Punch object is added to Store's Punches relation"},
        {'test_name': "Punch's Patron pointer is set"},
        {'test_name': "Punch's  punches is set to correct amount"},
        {'test_name': "PatronStore's punch_count is updated"},
        {'test_name': "PatronStore's all_time_punches is updated"},
        
        {'test_name': "Using unused punch_code returns error with PATRON_NOT_FOUND"},
    ])
    
    globals()['emp_lifetime_punches'] = employee.lifetime_punches
    globals()['patron_store'] = PatronStore.objects().get(\
        Patron=patron.objectId, Store=store.objectId)
    
    ##########  Punch creates a new Punch object (from employee)
    def test_0():
        if Punch.objects().count(Patron=patron.objectId) > 0:
            return "Punches for the Store exists. Test is invalid."
            
        cloud_call("punch", {
            "punch_code": patron.punch_code,
            "num_punches": 1,
            "store_id": store.objectId,
            "store_name": store.store_name,
            "employee_id": employee.objectId,
        })
    
        return Punch.objects().count(Patron=patron.objectId) == 1
    
    ##########  Punch object is added to Store's Punches relation 
    def test_1():
        punch = Punch.objects().get(Patron=patron.objectId)
        globals()['punch'] = punch
        return store.get("punches", objectId=punch.objectId,
            limit=0, count=1) == 1
    
    ##########  Punch object is added to Employee's Punches relation
    def test_2():
        return employee.get("punches",
            objectId=globals()['punch'].objectId,
            limit=0, count=1) == 1
    
    ##########  Punch's Patron pointer is set
    def test_3():
        return globals()['punch'].Patron == patron.objectId
    
    ##########  Punch's punches is set to correct amount
    def test_4():
        return globals()['punch'].punches == 1
    
    ##########  Employee's lifetime_punches is updated
    def test_5():
        employee.lifetime_punches = None
        return globals()['emp_lifetime_punches']+1 ==\
            employee.get("lifetime_punches")
    
    ##########  PatronStore is created since it does not yet exist
    def test_6():
        if globals()['patron_store'] is not None:
            return "PatronStore already existed. Test is invalid."
            
        return PatronStore.objects().count(\
            Patron=patron.objectId, Store=store.objectId) == 1
    
    ##########  PatronStore is added to Patron's PatronStores relation
    def test_7():
        patron_store = PatronStore.objects().get(\
            Patron=patron.objectId, Store=store.objectId)
        globals()['patron_store'] = patron_store
        return patron.get("patronStores", objectId=patron_store.objectId,
            limit=0, count=1) == 1
    
    ##########  PatronStore is added to Store's PatronStores relation
    def test_8():
        return store.get("patronStores", objectId=globals()['patron_store'].objectId,
            limit=0, count=1) == 1
    
    ##########  PatronStore's Patron pointer is set
    def test_9():
        return globals()['patron_store'].Patron is not None
    
    ##########  PatronStore's Store pointer is set 
    def test_10():
        return globals()['patron_store'].Store is not None
    
    ##########  PatronStore's all_time_punches is set to amount given
    def test_11():
        return globals()['patron_store'].all_time_punches == 1
    
    ##########  PatronStore's punch_count is set to amount given
    def test_12():
        return globals()['patron_store'].punch_count == 1
    
    ##########  PatronStore's pending_reward is set to false 
    def test_13():
        return not globals()['patron_store'].pending_reward
    
    
    ##########  Punch creates a new Punch object (from dashboard - owner)
    def test_14():
        globals()['punch'].delete()
        if Punch.objects().count(Patron=patron.objectId) > 0:
            return "Punches for the Store exists. Test is invalid."
        
        cloud_call("punch", {
            "punch_code": patron.punch_code,
            "num_punches": 1,
            "store_id": store.objectId,
            "store_name": store.store_name,
        })
    
        return Punch.objects().count(Patron=patron.objectId) == 1
    
    ##########  Punch object is added to Store's Punches relation
    def test_15():
        punch = Punch.objects().get(Patron=patron.objectId)
        globals()['punch'] = punch
        return store.get("punches", objectId=punch.objectId,
            count=1, limit=0) == 1
   
    ##########  Punch's Patron pointer is set
    def test_16():
        return globals()['punch'].Patron == patron.objectId
    
    ##########  Punch's punches is set to correct amount 
    def test_17():
        return globals()['punch'].punches == 1
    
    ##########  PatronStore's punch_count is updated 
    def test_18():
        patron_store = globals()['patron_store']
        patron_store.fetch_all(clear_first=True, with_cache=False)
        return patron_store.punch_count == 2
    
    ##########  PatronStore's all_time_punches is updated 
    def test_19():
        return globals()['patron_store'].all_time_punches == 2
        
    ##########  Using unused punch_code returns error with PATRON_NOT_FOUND 
    def test_20():
        res = cloud_call("punch", {
            "punch_code": "xxxxx",
            "num_punches": 1,
            "store_id": store.objectId,
            "store_name": store.store_name,
        })
    
        return res["error"] == "PATRON_NOT_FOUND"
    
    for i in range(21):
        test.testit(locals()["test_%s" % (str(i),)])
        
    # END OF ALL TESTS - cleanup
    return test.get_results()
