"""
Tests for punch.
"""

from parse.utils import cloud_call
from cloud_code.tests import CloudCodeTest
from parse.apps.accounts.models import Account

# This User exists solely for testing CloudCode.
# It must have a Store and Patron pointers.
ACCOUNT_EMAIL = "cloudcode@repunch.com"

def test_punch():
    """
    This first deletes all the PatronStores in the Store's PatronStore relation.
    """
    account = Account.objects().get(email=ACCOUNT_EMAIL,
        include="Patron,Store")
    patron = account.patron
    store = account.store
    
    if store.get("patronStores"):
        for ps in store.patronStores:
            ps.delete()
        
    store.patronStores = None
    
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
        {'test_name': "PatronStore's all_time_punches is set to 0"},
        {'test_name': "PatronStore's punch_count is set to 0"},
        {'test_name': "PatronStore's pending_reward is set to false"},
        
        {'test_name': "Punch creates a new Punch object (from dashboard - owner)"},
        {'test_name': "Punch object is added to Store's Punches relation"},
        {'test_name': "Patron pointer is set"},
        {'test_name': "Punches is set to correct amount"},
        {'test_name': "PatronStore's punch_count is updated"},
        {'test_name': "PatronStore's all_time_punches is updated"},
        
        {'test_name': "Using unused punch_code returns error with PATRON_NOT_FOUND"},
    ])
    
    
    ##########  Punch creates a new Punch object (from employee) TODO
    def test_0():
        return True # TODO
    
    test.testit(test_0)
    
    ##########  Punch object is added to Store's Punches relation TODO
    ##########  Punch object is added to Employee's Punches relation TODO
    ##########  Patron pointer is set TODO
    ##########  Punches is set to correct amount TODO
    ##########  Employee's life_time_punches is updated TODO
    ##########  PatronStore is created since it does not yet exist TODO
    ##########  PatronStore is added to Patron's PatronStores relation TODO
    ##########  PatronStore is added to Store's PatronStores relation TODO
    ##########  PatronStore's Patron pointer is set TODO
    ##########  PatronStore's Store pointer is set TODO
    ##########  PatronStore's all_time_punches is set to 0 TODO
    ##########  PatronStore's punch_count is set to 0 TODO
    ##########  PatronStore's pending_reward is set to false TODO
        
    ##########  Punch creates a new Punch object (from dashboard - owner) TODO
    ##########  Punch object is added to Store's Punches relation TODO
    ##########  Patron pointer is set TODO
    ##########  Punches is set to correct amount TODO
    ##########  PatronStore's punch_count is updated TODO
    ##########  PatronStore's all_time_punches is updated TODO
        
    ##########  Using unused punch_code returns error with PATRON_NOT_FOUND TODO
    
