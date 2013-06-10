"""
Parse equivalence of Django apps.messages.models
"""

from importlib import import_module

from parse.core.models import ParseObject
from parse.apps.messages import DRAFT, UNREAD

class Message(ParseObject):
    """ Equivalence class of apps.messages.models.Message """

    # message_types
    FEEDBACK = "feedback"
    GIFT = "gift"
    RETAILER = "retailer"
    
    def __init__(self, **data):
        self.subject = data.get("subject")
        self.body = data.get("body")
        self.offer_title = data.get("offer_title")
        self.date_offer_expiration = data.get('date_offer_expiration')
        self.message_type = data.get("message_type")
        self.is_read = data.get("is_read", False)
        # store name or patron fullname
        self.sender_name = data.get("sender_name")
        # empty messages sent by patrons
        self.store_id = data.get("store_id")
    
        self.Reply = data.get("Reply")

        # NOT IN SERVER SIDE
        # reward_title = string
        # reward_description = string
        # reward_id = string
        # reward_punches = interger
        # ---------------

        super(Message, self).__init__(False, **data)

    def get_absolute_url(self):
		return reverse('message_edit', args=[self.objectId])

    def get_class(self, className):
        """ note that a reply/feedback is also a message """
        if className == "Reply":
            return Message
