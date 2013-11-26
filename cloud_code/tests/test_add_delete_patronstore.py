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


class TestAddDeletePatronStore(CloudCodeTest):
    """
    This first deletes all the PatronStores that points to this Store.
    """

    def __init__(self):
        super(TestAddDeletePatronStore, self).__init__((
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
        ))
            
        self.account = Account.objects().get(email=ACCOUNT_EMAIL,
            include="Patron,Store")
        self.patron = self.account.patron
        self.store = self.account.store
    
        for ps in PatronStore.objects().filter(Store=self.store.objectId):
            ps.delete()
    
    def test_0(self):
        """
        Add_patronstore creates a new PatronStore if does not exist
        """
        if PatronStore.objects().count(Patron=self.patron.objectId,
            Store=self.store.objectId) == 1:
            return "PatronStore already exists. Test is invalid."
            
        cloud_call("add_patronstore", {
            "patron_id": self.patron.objectId,
            "store_id": self.store.objectId,
        })
        
        return PatronStore.objects().count(Patron=self.patron.objectId,
            Store=self.store.objectId) == 1
    
    def test_1(self):
        """
        PatronStore is added to Patron's PatronStores relation
        """
        self.patron_store = PatronStore.objects().get(\
            Patron=self.patron.objectId, Store=self.store.objectId)
        return self.patron.get("patronStores", count=1, limit=0,
            objectId=self.patron_store.objectId) == 1
    
    def test_2(self):
        """
        PatronStore is added to Store's PatronStores relation
        """
        return self.store.get("patronStores", count=1, limit=0,
            objectId=self.patron_store.objectId) == 1
    
    def test_3(self):
        """
        PatronStore's Patron pointer is set
        """
        return self.patron_store.Patron == self.patron.objectId
    
    def test_4(self):
        """
        PatronStore's Store pointer is set 
        """
        return self.patron_store.Store == self.store.objectId
    
    def test_5(self):
        """
        PatronStore's all_time_punches is set to 0 
        """
        return self.patron_store.all_time_punches == 0
    
    def test_6(self):
        """
        PatronStore's punch_count is set to 0 
        """
        return self.patron_store.punch_count == 0
    
    def test_7(self):
        """
        PatronStore's pending_reward is set to false 
        """
        return not self.patron_store.pending_reward
        
    def test_8(self):
        """
        Add_patronstore returns existing PatronStore
        """
        if PatronStore.objects().count(\
            objectId=self.patron_store.objectId) == 0:
            return "PatronStore does not exists. Test is invalid."
            
        cloud_call("add_patronstore", {
            "patron_id": self.patron.objectId,
            "store_id": self.store.objectId,
        })
        
        return PatronStore.objects().count(Patron=self.patron.objectId,
            Store=self.store.objectId) == 1 and\
            PatronStore.objects().get(Patron=self.patron.objectId,
            Store=self.store.objectId).objectId == self.patron_store.objectId
    
    def test_9(self):
        """
        PatronStore is in the Patron's PatronStores relation
        """
        self.patron_store = PatronStore.objects().get(\
            Patron=self.patron.objectId, Store=self.store.objectId)
        return self.patron.get("patronStores", count=1, limit=0,
            objectId=self.patron_store.objectId) == 1
    
    def test_10(self):
        """
        PatronStore is in the Store's PatronStores relation 
        """
        return self.store.get("patronStores", count=1, limit=0,
            objectId=self.patron_store.objectId) == 1
    
    def test_11(self):
        """
        Delete_patronstore deletes the PatronStore 
        """
        if PatronStore.objects().count(\
            objectId=self.patron_store.objectId) == 0:
            return "PatronStore does not exists. Test is invalid."
    
        cloud_call("delete_patronstore", {
            "patron_store_id": self.patron_store.objectId,
            "patron_id": self.patron.objectId,
            "store_id": self.store.objectId,
        })
        
        return PatronStore.objects().count(\
            objectId=self.patron_store.objectId) == 0
    
    def test_12(self):
        """
        PatronStore is removed from the Patron's PatronStores relation 
        """
        return self.patron.get("patronStores", count=1, limit=0,
            objectId=self.patron_store.objectId) == 0
    
    def test_13(self):
        """
        PatronStore is removed from the Store's PatronStores relation 
        """
        return self.store.get("patronStores", count=1, limit=0,
            objectId=self.patron_store.objectId) == 0
    
