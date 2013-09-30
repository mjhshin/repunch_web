"""
Parse equivalence of Django apps.messages.models
"""

from django.core.urlresolvers import reverse
from importlib import import_module

from parse.core.models import ParseObject

class Message(ParseObject):
    """ Equivalence class of apps.messages.models.Message """    
    def __init__(self, **data):
        self.subject = data.get("subject")
        self.body = data.get("body")
        self.offer_title = data.get("offer_title")
        self.date_offer_expiration = data.get('date_offer_expiration')
        self.message_type = data.get("message_type")
        # can be all, idle, most_loyal
        self.filter = data.get("filter")
        # only used by stores
        self.is_read = data.get("is_read", False)
        # store name or patron fullname
        self.sender_name = data.get("sender_name")
        # empty if message sent by patron??? required atm
        self.store_id = data.get("store_id")
        # empty if message sent by store
        self.patron_id = data.get('patron_id')
        # number of patrons that received this message
        self.receiver_count = data.get("receiver_count")
        
        # not used by the dashboard
        self.gift_description = data.get("gift_description")
        self.gift_title = data.get("gift_title")
    
        self.Reply = data.get("Reply")
        # meta for Reply pointer
        self._reply = "Message"

        super(Message, self).__init__(False, **data)
        
    @classmethod  
    def fields_required(cls):
        """
        See ParseObject for documentation.
        """
        return (cls, "body", "message_type", "sender_name",
            "store_id", ("subject", {"message_type": "feedback"}),
            ("gift_title", "gift_description"),
            ("offer_title", "date_offer_expiration") )

    def get_absolute_url(self):
		return reverse('message_details', args=[self.objectId])

    def get_class(self, className):
        """ note that a reply/feedback is also a message """
        if className == "Message":
            return Message
            
class MessageStatus(ParseObject):
    """ 
    This is a simple wrapper around Message. 
    This is used by patrons since a message they received from a store
    is shared by other patrons.
    """
    def __init__(self, **data):
        self.is_read = data.get("is_read", False)
        self.redeem_available = data.get("redeem_available")
        
        self.Message  = data.get("Message")
        
        super(MessageStatus, self).__init__(False, **data)
        
    @classmethod  
    def fields_required(cls):
        """
        See ParseObject for documentation.
        """
        return (cls, "is_read", "redeem_available", "Message")

    def get_class(self, className):
        if className == "Message":
            return Message
