"""
Tests for request, validate, and reject redeem.
"""

from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from cloud_code.tests import CloudCodeTest
from parse.utils import cloud_call
from parse.apps.patrons.models import PatronStore
from parse.apps.rewards.models import RedeemReward
from parse.apps.messages.models import Message

class TestRequestValidateRejectRedeem(CloudCodeTest):
    """
    This first deletes all the PatronStores that points to this Store.
    This will also set the Store's rewards, sentMessages, redeemRewards,
    and the Patron's receivedMessages.
    """
    
    def __init__(self, verbose=False):
        super(TestRequestValidateRejectRedeem, self).__init__(verbose=verbose)
    
        self.store.rewards = [{
            "reward_id":0,
            "redemption_count":0,
            "punches":1,
            "reward_name":"ATest Reward",
            "description":"Test Reward",
        }]
        self.store.update()
        self.reward = self.store.rewards[0]
    
        if self.store.get("sentMessages"):
            for m in self.store.sentMessages:
                m.delete()
            self.store.sentMessages = None
            
        if self.store.get("redeemRewards"):
            for r in self.store.redeemRewards:
                r.delete()
            self.store.redeemRewards = None
            
        if self.patron.get("receivedMessages"):
            for ms in self.patron.receivedMessages:
                ms.delete()
            self.patron.receivedMessages = None
        
        for ps in PatronStore.objects().filter(Store=self.store.objectId):
            ps.delete()
        
        self.patron_store = self.add_patronstore()
    
    def add_patronstore(self, punch_count=10):
        patron_store = PatronStore(**cloud_call("add_patronstore", {
            "patron_id": self.patron.objectId,
            "store_id": self.store.objectId,
        })["result"])
        
        patron_store.all_time_punches = punch_count
        patron_store.punch_count = punch_count
        patron_store.update()
        return patron_store
        
    def request_redeem(self, reward_id=False, title=False,
        message_status_id=None):
        
        if type(reward_id) is bool:
            reward_id = self.reward["reward_id"]
            
        if type(title) is bool:
            title = self.reward["reward_name"]
            
        return cloud_call("request_redeem", {
            "patron_id": self.patron.objectId,
            "store_id": self.store.objectId,
            "patron_store_id": self.patron_store.objectId,
            "reward_id": reward_id,
            "num_punches": self.reward["punches"],
            "name": self.patron.get_fullname(),
            "title": title,
            "message_status_id": message_status_id,
        })
    
    def create_offer(self):
        offer = Message.objects().create(**{
            'subject': u'test_request_validate_redeem script message offer',
            'body': u'test_request_validate_redeem script generate offer', 
            'sender_name': u'test_request_validate_redeem', 
            'store_id': self.store.objectId, 
            'is_read': False, 
            'offer_redeemed': False, 
            'date_offer_expiration': timezone.now()+relativedelta(days=1), 
            'filter': u'all', 
            'offer_title': u'test_request_validate_redeem script offer', 
            'message_type': 'offer', 
        })
        
        cloud_call("retailer_message", {
            "filter": offer.filter,
            "store_name": self.store.store_name,
            "message_id": offer.objectId,
            "store_id": self.store.objectId,
            "subject": offer.subject,
        })
        
        return offer
    
    def test_0(self):
        """
        Request_redeem creates a new RedeemReward (reward)
        """
        if RedeemReward.objects().count(\
            PatronStore=self.patron_store.objectId) > 0:
            return "PatronStore exists. Test is invalid."
        
        self.request_redeem()
        
        return RedeemReward.objects().count(\
            PatronStore=self.patron_store.objectId) == 1
    
    def test_1(self):
        """
        RedeemReward is added to Store's RedeemReward relation
        """
        self.redeem_reward = RedeemReward.objects().get(\
                PatronStore=self.patron_store.objectId)
        return self.store.get("redeemRewards", objectId=\
            self.redeem_reward.objectId, count=1, limit=0) == 1
    
    def test_2(self):
        """
        PatronStore's pending_reward is set to true
        """
        self.patron_store.fetch_all(clear_first=True, with_cache=False)
        return self.patron_store.pending_reward
    
    def test_3(self):
        """
        RedeemReward's patron_id is set 
        """
        return self.redeem_reward.patron_id == self.patron.objectId
    
    def test_4(self):
        """
        RedeemReward's customer_name is set
        """
        return self.redeem_reward.customer_name ==\
            self.patron.get_fullname()
    
    def test_5(self):
        """
        RedeemReward's is_redeemed is set to false
        """
        return not self.redeem_reward.is_redeemed
    
    def test_6(self):
        """
        RedeemReward's title is set
        """
        return self.redeem_reward.title == self.reward["reward_name"]
    
    def test_7(self):
        """
        RedeemReward's PatronStore pointer is set 
        """
        return self.redeem_reward.PatronStore ==\
            self.patron_store.objectId
    
    def test_8(self):
        """
        RedeemReward's num_punches is set 
        """
        return self.redeem_reward.num_punches == self.reward["punches"]
    
    def test_9(self):
        """
        RedeemReward's reward_id is set 
        """
        return self.redeem_reward.reward_id == self.reward["reward_id"]
        
    def test_10(self):
        """
        Validate_redeem successful
        """
        self.pt_punch_cout_b4 = self.patron_store.punch_count
        self.reward_red_count_b4 = self.reward["redemption_count"]
            
        res = cloud_call("validate_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
            "reward_id": self.reward["reward_id"],
        })
        
        return "error" not in res
    
    def test_11(self):
        """
        RedeemReward's is_redeemed is set to true
        """
        self.redeem_reward.fetch_all(clear_first=True, with_cache=False)
        self.patron_store.fetch_all(clear_first=True, with_cache=False)
        self.store.rewards = None
        self.reward = self.store.get("rewards")[0]
        return self.redeem_reward.is_redeemed
    
    def test_12(self):
        """
        PatronStore's pending_reward is set to false
        """
        return not self.patron_store.pending_reward
    
    def test_13(self):
        """
        PatronStore's punch_count is updated 
        """
        return self.patron_store.punch_count ==\
            self.pt_punch_cout_b4 - self.reward["punches"]
    
    def test_14(self):
        """
        The reward's redemption_count is updated 
        """
        return self.reward["redemption_count"] ==\
            self.reward_red_count_b4 + 1
    
    def test_15(self):
        """
        Reject_redeem successful
        """
        # need a new redeem
        self.request_redeem()
        self.redeem_reward = RedeemReward.objects().get(\
            PatronStore=self.patron_store.objectId, is_redeemed=False)
            
        res = cloud_call("reject_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
        })
        
        return "error" not in res
    
    def test_16(self):
        """
        RedeemReward is deleted
        """
        self.patron_store.fetch_all(clear_first=True, with_cache=False)
        return RedeemReward.objects().count(\
            objectId=self.redeem_reward.objectId) == 0
    
    def test_17(self):
        """
        PatronStore's pending_reward is set to false
        """
        return not self.patron_store.pending_reward
        
    def test_18(self):
        """
        Request_redeem creates a new RedeemReward (offer/gift)
        """
        # need to create an offer
        self.offer = self.create_offer()
        self.message_status =\
            self.patron.get("receivedMessages", limit=1)[0]
        self.patron.receivedMessages = None
        
        self.request_redeem(None, self.offer.offer_title,
            self.message_status.objectId)
        
        return RedeemReward.objects().count(\
            MessageStatus=self.message_status.objectId,
            is_redeemed=False) == 1
            
    def test_19(self):
        """
        RedeemReward is added to Store's RedeemReward relation
        """
        self.redeem_reward = RedeemReward.objects().get(\
            MessageStatus=self.message_status.objectId,
            is_redeemed=False)
            
        self.store.redeemRewards = None
        return self.store.get("redeemRewards", objectId=\
            self.redeem_reward.objectId, count=1, limit=0) == 1
        
    def test_20(self):
        """
        RedeemReward's num_punches is set to 0 regardless of input
        """
        return self.redeem_reward.num_punches == 0
    
    def test_21(self):
        """
        RedeemReward's MessageStatus is set
        """
        return self.redeem_reward.MessageStatus ==\
            self.message_status.objectId
    
    def test_22(self):
        """
        RedeemReward's patron_id is set
        """
        return self.redeem_reward.patron_id == self.patron.objectId
    
    def test_23(self):
        """
        RedeemReward's customer_name is set
        """
        return self.redeem_reward.customer_name ==\
            self.patron.get_fullname()
    
    def test_24(self):
        """
        RedeemReward's is_redeemed is set to false
        """
        return not self.redeem_reward.is_redeemed
    
    def test_25(self):
        """
        RedeemReward's title is set
        """
        return self.redeem_reward.title == self.offer.offer_title
    
    def test_26(self):
        """
        MessageStatus' redeem_available is set to pending
        """
        self.message_status.redeem_available = None
        return self.message_status.get("redeem_available") == "pending"
    
    def test_27(self):
        """
        Validate_redeem successful
        """
        res = cloud_call("validate_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
        })
        
        return "error" not in res
    
    def test_28(self):
        """"
        RedeemReward's is_redeemed is set to true
        """
        self.redeem_reward.fetch_all(clear_first=True, with_cache=False)
        self.message_status.fetch_all(clear_first=True, with_cache=False)
        
        return self.redeem_reward.is_redeemed
    
    def test_29(self):
        """
        MessageStatus's redeem_available is set to "no"
        """
        return self.message_status.redeem_available == "no"
            
    def test_30(self):
        """
        Reject_redeem successful
        """
        # create another redeem
        self.offer = self.create_offer()
        self.message_status = self.patron.get("receivedMessages",
            redeem_available="yes", limit=1)[0]
        self.patron.receivedMessages = None
        self.request_redeem(None, self.offer.offer_title,
            self.message_status.objectId)
        self.redeem_reward = RedeemReward.objects().get(\
                MessageStatus=self.message_status.objectId,
                is_redeemed=False)
            
        res = cloud_call("reject_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
        })
        return "error" not in res
    
    def test_31(self):
        """
        RedeemReward is deleted
        """
        return  RedeemReward.objects().count(\
            objectId=self.redeem_reward.objectId) == 0
    
    def test_32(self):
        """
        MessageStatus' redeem_available is set to "no"
        """
        self.message_status.redeem_available = None
        return self.message_status.get("redeem_available") == "no"
    
    def test_33(self):
        """
        Request_redeem succeeds with pending if
        PatronStore's pending_reward is true before the request.
        """
        self.patron_store.pending_reward = True
        self.patron_store.update()
        return self.request_redeem()["result"] == "pending"
            
    def test_34(self):
        """
        Validate_redeem succeeds with validated if the
        RedeemReward has already been redeemed
        """
        self.patron_store.pending_reward = False
        self.patron_store.update()
        self.request_redeem()
        self.redeem_reward = RedeemReward.objects().get(\
            PatronStore=self.patron_store.objectId, is_redeemed=False)
        self.redeem_reward.is_redeemed = True
        self.redeem_reward.update()
        
        return cloud_call("validate_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
            "reward_id": self.reward["reward_id"]
        })["result"]["code"] == "validated"
    
    def test_35(self):
        """
        Validate_redeem succeeds with PATRONSTORE_REMOVED if the
        PatronStore has been deleted
        """
        self.redeem_reward.is_redeemed = False
        self.redeem_reward.update()
        self.patron_store.delete()
        
        return cloud_call("validate_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
            "reward_id": self.reward["reward_id"]
        })["result"]["code"] == "PATRONSTORE_REMOVED"
    
    def test_36(self):
        """
        The RedeemReward is then deleted
        """
        return  RedeemReward.objects().count(\
            objectId=self.redeem_reward.objectId) == 0
        
    def test_37(self):
        """
        Validate_redeem succeeds with insufficient if the
        PatronStore does not have enough punches
        """
        self.patron_store = self.add_patronstore(0)
        self.request_redeem()
        self.redeem_reward = RedeemReward.objects().get(\
            PatronStore=self.patron_store.objectId, is_redeemed=False)
            
        return cloud_call("validate_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
            "reward_id": self.reward["reward_id"]
        })["result"]["code"] == "insufficient"
    
    def test_38(self):
        """
        The RedeemReward is then deleted
        """
        return  RedeemReward.objects().count(\
            objectId=self.redeem_reward.objectId) == 0
        
    def test_39(self):
        """
        Validate_redeem fails with REDEEMREWARD_NOT_FOUND if the
        RedeemReward has been deleted
        """
        self.redeem_reward.delete()
        return cloud_call("validate_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
            "reward_id": self.reward["reward_id"]
        })["error"] == "REDEEMREWARD_NOT_FOUND"
            
    def test_40(self):
        """
        Reject_redeem fails with REDEEMREWARD_VALIDATED
        if the RedeemReward has already been validated
        """
        self.patron_store.all_time_punches = 10
        self.patron_store.punch_count = 10
        self.patron_store.update()
        self.request_redeem()
        self.redeem_reward = RedeemReward.objects().get(\
            PatronStore=self.patron_store.objectId, is_redeemed=False)
        self.redeem_reward.is_redeemed = True
        self.redeem_reward.update()
        
        return cloud_call("reject_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
        })["error"] == "REDEEMREWARD_VALIDATED"
    
    def test_41(self):
        """
        Reject_redeem fails with REDEEMREWARD_NOT_FOUND if the
        RedeemReward has been deleted 
        """
        self.patron_store.pending = False
        self.patron_store.update()
        self.request_redeem()
        self.redeem_reward = RedeemReward.objects().get(\
            PatronStore=self.patron_store.objectId, is_redeemed=False)
        self.redeem_reward.delete()
        
        return cloud_call("reject_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
        })["error"] == "REDEEMREWARD_NOT_FOUND"
    
    def test_42(self):
        """
        Reject_redeem fails with PATRONSTORE_REMOVED if the
        PatronStore has been deleted
        """
        self.patron_store.pending = False
        self.patron_store.update()
        self.request_redeem()
        self.redeem_reward = RedeemReward.objects().get(\
            PatronStore=self.patron_store.objectId, is_redeemed=False)
        self.patron_store.delete()
        
        return cloud_call("reject_redeem", {
            "redeem_id": self.redeem_reward.objectId,
            "store_id": self.store.objectId,
        })["error"] == "PATRONSTORE_REMOVED"
    
    def test_43(self):
        """
        The RedeemReward is then deleted 
        """
        return  RedeemReward.objects().count(\
            objectId=self.redeem_reward.objectId) == 0
            
