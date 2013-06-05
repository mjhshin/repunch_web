"""
Parse equivalence of Django apps.messages.models
"""

from importlib import import_module

from parse.core.models import ParseObject
from parse.apps.messages import DRAFT, UNREAD

class Message(ParseObject):
    """ Equivalence class of apps.messages.models.Message """
    
    def __init__(self, **data):
        self.date_sent = data.get('date_sent')
        self.subject = data.get('subject')
        self.status = data.get('status', DRAFT)
        self.message = data.get('message')
        self.send_to_group = data.get('send_to_group', DRAFT)
        self.sent_to_recipients_count = data.get('sent_to_recipients_count', 0)
        self.attach_offer = data.get('attach_offer', False)
        self.offer_title = data.get('offer_title')
        self.offer_expiration = data.get('offer_expiration')

        self.Store = data.get("Store")

        super(Message, self).__init__(False, **data)

    def get_absolute_url(self):
		return reverse('message_edit', args=[self.objectId])

    def get_class(self, className):
        if className == "Store":
            return getattr(import_module('parse.apps.stores.models'),
                                className)

class Feedback(ParseObject):
    """ Equivalence class of apps.messages.models.Feedback """
    
    def __init__(self, **data):
        self.subject = data.get("subject")
        self.message = data.get("message")
        self.is_response = data.get("is_response", False)
        self.status = data.get("status", UNREAD)

        self.Patron = data.get("Patron")
        # parent = models.ForeignKey('self', null=True, blank=True)
        self.Feedback = data.get("Feedback") 
        self.Store = data.get("Store")

        super(Feedback, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Store":
            return getattr(import_module('parse.apps.stores.models'),
                                className)
        elif className == "Patron":
            return getattr(import_module('parse.apps.patrons.models'),
                                className)
        elif className == "Feedback":
            return self.__class__

    def get_absolute_url(self):
		# the details are based on the parent (main) message
		if not self.Parent:
			return reverse('feedback_details', args=[self.objectId])
		return reverse('feedback_details', args=[self.get("parent").objectId])

    def thread_count(self):
		return Feedback.objects().count(Feedback=self.objectId)












