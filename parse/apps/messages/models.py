"""
Parse equivalence of Django apps.messages.models
"""

from datetime import date
from json import dumps

from parse.utils import parse
from parse.core.models import ParseObject

class Message(ParseObject):
    """ Equivalence class of apps.messages.models.Message """
    DRAFT = "Draft"
    SENT = "Sent"
    ALL = "All"
    ONLY_ONE_PUNCH = "Only One Punch"
    
    def __init__(self, **data):
        self.date_added = data.get('date_added', date.today().isoformat())
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

        super(Message, self).__init__(**data)

    def get_absolute_url(self):
		return reverse('message_edit', args=[self.objectId])


class Feedback(ParseObject):
    """ Equivalence class of apps.messages.models.Feedback """
    READ = "Read"
    UNREAD = "Unread"
    
    def __init__(self, **data):
        self.date_added = data.get('date_added', date.today().isoformat())
        self.subject = data.get("subject")
        self.message = data.get("message")
        self.is_response = data.get("is_response", False)
        self.status = data.get("status", UNREAD)

        self.Patron = data.get("Patron")
        self.Parent = data.get("Parent") 
        self.Store = data.get("Store")

        super(Feedback, self).__init__(**data)

    def get_absolute_url(self):
		# the details are based on the parent (main) message
		if not self.Parent:
			return reverse('feedback_details', args=[self.objectId])
		return reverse('feedback_details', args=[self.get("parent").objectId])

    def thread_count(self):
		return parse("GET", self.path(), query={"where":json.dumps({
               "Parent":self.objectId}),"count":1,"limit":0})["count"]












