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
    This first deletes all the PatronStores in the Store's PatronStore relation.
    All Punch objects for the Account's Store are deleted.
    """
    account = Account.objects().get(email=ACCOUNT_EMAIL,
        include="Patron,Store,Employee")
    patron = account.patron
    store = account.store
    employee = account.employee
    
    if store.get("patronStores"):
        for ps in store.patronStores:
            ps.delete()
        store.patronStores = None
    
    for punch in Punch.objects().filter(Store=store.objectId):
        punch.delete()
    
    test = CloudCodeTest("PUNCH", [
        {'test_name': "Punch creates a new Punch object (from employee)"},
        {'test_name': "Punch object is added to Store's Punches relation"},
        {'test_name': "Punch object is added to Employee's Punches relation"},
        {'test_name': "Patron pointer is set"},
        {'test_name': "Punches is set to correct amount"},
        {'test_name': "Employee's life_time_punches is updated"},
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
        {'test_name': "Patron pointer is set"},
        {'test_name': "Punches is set to correct amount"},
        {'test_name': "PatronStore's punch_count is updated"},
        {'test_name': "PatronStore's all_time_punches is updated"},
        
        {'test_name': "Using unused punch_code returns error with PATRON_NOT_FOUND"},
    ])
    
    emp_lifetime_punches = employee.life_time_punches
    patron_store = PatronStore.objects().get(\
        Patron=patron.objectId, Store=store.objectId)
    
    ##########  Punch creates a new Punch object (from employee)
    def test_0():
        if Punch.objects().count(Store=store.objectId) > 0:
            return "Punches for the Store exists. Test is invalid."
            
        cloud_call("punch", {
            "punch_code": patron.punch_code,
            "num_punches": 1,
            "store_id": store.objectId,
            "store_name": store.store_name,
            "employee_id": employee.objectId,
        })
    
        return Punch.objects().count(Store=store.objectId) == 1
    
    test.testit(test_0)
    
    punch = Punch.objects().get()
    
    ##########  Punch object is added to Store's Punches relation 
    def test_1():
        return store.get("punches", objectId=punch.objectId,
            limit=0, count=1) == 1
    
    test.testit(test_1)
    
    ##########  Punch object is added to Employee's Punches relation
    def test_2():
        return employee.get("punches", objectId=punch.objectId,
            limit=0, count=1) == 1
    
    test.testit(test_2)
    
    ##########  Patron pointer is set
    def test_3():
        return punch.Patron is not None
    
    test.testit(test_3)
    
    ##########  Punches is set to correct amount
    def test_4():
        return punch.punches == 1
    
    test.testit(test_4)
    
    ##########  Employee's life_time_punches is updated
    def test_5():
        employee.life_time_punches = None
        return emp_lifetime_punches+1 == employee.get("life_time_punches")
    
    test.tesit(test_5)
    
    ##########  PatronStore is created since it does not yet exist
    def test_6():
        if patron_store is not None:
            return "PatronStore already existed. Test is invalid."
            
        return PatronStore.objects().count(\
            Patron=patron.objectId, Store=store.objectId)
    
    test.testit(test_6)
    
    patron_store = PatronStore.objects().get(\
        Patron=patron.objectId, Store=store.objectId)
    
    ##########  PatronStore is added to Patron's PatronStores relation
    def test_7():
        return patron.get("patronStores", objectId=patron_store.objectId,
            limit=0, count=1) == 1
    
    test.testit(test_7)
    
    
    ##########  PatronStore is added to Store's PatronStores relation
    def test_8():
        return store.get("patronStores", objectId=patron_store.objectId,
            limit=0, count=1) == 1
    
    test.testit(test_8)
    
    ##########  PatronStore's Patron pointer is set
    def test_9():
        return patron_store.Patron is not None
    
    test.testit(test_9)
    
    ##########  PatronStore's Store pointer is set 
    def test_10():
        return patron_store.Store is not None
    
    test.testit(test_10)
    
    ##########  PatronStore's all_time_punches is set to amount given
    def test_11():
        return patron_store.all_time_punches == 1
    
    test.testit(test_11)
    
    ##########  PatronStore's punch_count is set to amount given
    def test_12():
        return patron_store.punch_count == 1
    
    test.testit(test_12)
    
    ##########  PatronStore's pending_reward is set to false 
    def test_13():
        return not patron_store.pending_reward
    
    test.testit(test_13)
    
    ##########  Punch creates a new Punch object (from dashboard - owner) TODO
    ##########  Punch object is added to Store's Punches relation TODO
    ##########  Patron pointer is set TODO
    ##########  Punches is set to correct amount TODO
    ##########  PatronStore's punch_count is updated TODO
    ##########  PatronStore's all_time_punches is updated TODO
        
    ##########  Using unused punch_code returns error with PATRON_NOT_FOUND TODO
    
