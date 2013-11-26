"""
Tests for punch.
"""

from parse.utils import cloud_call
from cloud_code.tests import CloudCodeTest
from parse.apps.rewards.models import Punch
from parse.apps.patrons.models import PatronStore

class TestPunch(CloudCodeTest):
    """
    This first deletes all the PatronStores that points to this Store.
    All Punch objects for the Account's Patron are deleted.
    """

    def __init__(self):
        super(TestPunch, self).__init__()
    
        for ps in PatronStore.objects().filter(Store=self.store.objectId):
            ps.delete()
        
        for punch in Punch.objects().filter(Patron=self.patron.objectId):
            punch.delete()
        
        self.emp_lifetime_punches = self.employee.lifetime_punches
        self.patron_store = PatronStore.objects().get(\
            Patron=self.patron.objectId, Store=self.store.objectId)
    
    def test_0(self):
        """
        Punch creates a new Punch object (from employee)
        """
        if Punch.objects().count(Patron=self.patron.objectId) > 0:
            return "Punches for the Store exists. Test is invalid."
            
        cloud_call("punch", {
            "punch_code": self.patron.punch_code,
            "num_punches": 1,
            "store_id": self.store.objectId,
            "store_name": self.store.store_name,
            "employee_id": self.employee.objectId,
        })
    
        return Punch.objects().count(Patron=self.patron.objectId) == 1
    
    def test_1(self):
        """
        Punch object is added to Store's Punches relation 
        """
        self.punch = Punch.objects().get(Patron=self.patron.objectId)
        return self.store.get("punches", objectId=self.punch.objectId,
            limit=0, count=1) == 1
    
    def test_2(self):
        """
        Punch object is added to Employee's Punches relation
        """
        return self.employee.get("punches", objectId=self.punch.objectId,
            limit=0, count=1) == 1
    
    def test_3(self):
        """
        Punch's Patron pointer is set
        """
        return self.punch.Patron == self.patron.objectId

    def test_4(self):
        """
        Punch's punches is set to correct amount
        """
        return self.punch.punches == 1
    
    def test_5(self):
        """
        Employee's lifetime_punches is updated
        """
        self.employee.lifetime_punches = None
        return self.emp_lifetime_punches + 1 ==\
            self.employee.get("lifetime_punches")
    
    def test_6(self):
        """
        PatronStore is created since it does not yet exist
        """
        if self.patron_store is not None:
            return "PatronStore already existed. Test is invalid."
            
        return PatronStore.objects().count(Patron=\
            self.patron.objectId, Store=self.store.objectId) == 1
    
    def test_7(self):
        """
        PatronStore is added to Patron's PatronStores relation
        """
        self.patron_store = PatronStore.objects().get(\
            Patron=self.patron.objectId, Store=self.store.objectId)
        return self.patron.get("patronStores", objectId=\
            self.patron_store.objectId, limit=0, count=1) == 1
    
    def test_8(self):
        """
        PatronStore is added to Store's PatronStores relation
        """
        return self.store.get("patronStores", objectId=\
            self.patron_store.objectId, limit=0, count=1) == 1
    
    def test_9(self):
        """
        PatronStore's Patron pointer is set
        """
        return self.patron_store.Patron is not None
    
    def test_10(self):
        """
        PatronStore's Store pointer is set 
        """
        return self.patron_store.Store is not None
    
    def test_11(self):
        """
        PatronStore's all_time_punches is set to amount given
        """
        return self.patron_store.all_time_punches == 1
    
    def test_12(self):
        """
        PatronStore's punch_count is set to amount given
        """
        return self.patron_store.punch_count == 1
    
    def test_13(self):
        """
        PatronStore's pending_reward is set to false 
        """
        return not self.patron_store.pending_reward
    
    def test_14(self):
        """
        Punch creates a new Punch object (from dashboard - owner)
        """
        self.punch.delete()
        if Punch.objects().count(Patron=self.patron.objectId) > 0:
            return "Punches for the Store exists. Test is invalid."
        
        cloud_call("punch", {
            "punch_code": self.patron.punch_code,
            "num_punches": 1,
            "store_id": self.store.objectId,
            "store_name": self.store.store_name,
        })
    
        return Punch.objects().count(Patron=self.patron.objectId) == 1
    
    def test_15(self):
        """
        Punch object is added to Store's Punches relation
        """
        self.punch = Punch.objects().get(Patron=self.patron.objectId)
        return self.store.get("punches", objectId=self.punch.objectId,
            count=1, limit=0) == 1
   
    def test_16(self):
        """
        Punch's Patron pointer is set
        """
        return self.punch.Patron == self.patron.objectId
    
    def test_17(self):
        """
        Punch's punches is set to correct amount 
        """
        return self.punch.punches == 1
    
    def test_18(self):
        """
        PatronStore's punch_count is updated 
        """
        self.patron_store.fetch_all(clear_first=True, with_cache=False)
        return self.patron_store.punch_count == 2
    
    def test_19(self):
        """
        PatronStore's all_time_punches is updated 
        """
        return self.patron_store.all_time_punches == 2
        
    def test_20(self):
        """
        Using unused punch_code returns error with PATRON_NOT_FOUND 
        """
        res = cloud_call("punch", {
            "punch_code": "xxxxx",
            "num_punches": 1,
            "store_id": self.store.objectId,
            "store_name": self.store.store_name,
        })
    
        return res["error"] == "PATRON_NOT_FOUND"
        
