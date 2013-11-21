"""
Tests for add_patronstore and delete_patronstore.
"""

from parse.utils import cloud_call
from cloud_code import CloudCodeTest

# The patron store created from the below are temporary.
# This means it gets deleted.
PATRON_ID = 
STORE_ID = 

def test_add_delete_patron_store():
    """
    This test also calls punch.
    """
    test = CloudCodeTest("ADD_DELETE_PATRONSTORE", [
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
        ###
        {'test_name': "Punch creates a new PatronStore if does not exist"},
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
    
    ##########  Add_patronstore creates a new PatronStore if does not exist TODO
    ##########  PatronStore is added to Patron's PatronStores relation TODO
    ##########  PatronStore is added to Store's PatronStores relation TODO
    ##########  PatronStore's Patron pointer is set TODO
    ##########  PatronStore's Store pointer is set TODO
    ##########  PatronStore's all_time_punches is set to 0 TODO
    ##########  PatronStore's punch_count is set to 0 TODO
    ##########  PatronStore's pending_reward is set to false TODO
        
    ##########  Add_patronstore returns existing PatronStore TODO
    ##########  PatronStore is in the Patron's PatronStores relation TODO
    ##########  PatronStore is in the Store's PatronStores relation TODO
        
    ##########  Delete_patronstore deletes the PatronStore TODO
    ##########  PatronStore is removed from the Patron's PatronStores relation TODO
    ##########  PatronStore is removed from the Store's PatronStores relation TODO
    
    ###
        
    ##########  Punch creates a new PatronStore if does not exist TODO
    ##########  PatronStore is added to Patron's PatronStores relation TODO
    ##########  PatronStore is added to Store's PatronStores relation TODO
    ##########  PatronStore's Patron pointer is set TODO
    ##########  PatronStore's Store pointer is set TODO
    ##########  PatronStore's all_time_punches is set to 0 TODO
    ##########  PatronStore's punch_count is set to 0 TODO
    ##########  PatronStore's pending_reward is set to false TODO
        
    ##########  Add_patronstore returns existing PatronStore TODO
    ##########  PatronStore is in the Patron's PatronStores relation TODO
    ##########  PatronStore is in the Store's PatronStores relation TODO
        
    ##########  Delete_patronstore deletes the PatronStore TODO
    ##########  PatronStore is removed from the Patron's PatronStores relation TODO
    ##########  PatronStore is removed from the Store's PatronStores relation TODO
    
    # END OF ALL TESTS - cleanup
    return results
