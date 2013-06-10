from django.db import models
from django.core.urlresolvers import reverse

from apps.stores.models import Store
from apps.patrons.models import Patron

class Message(models.Model):
    store = models.ForeignKey(Store)
    date_added = models.DateField(auto_now_add=True)
    date_sent = models.DateField(blank=True)
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=255,choices=(('Draft','Draft'),('Sent','Sent')),default='Draft')
    message = models.TextField()
    send_to_group = models.IntegerField(choices=((0,'All'), (1, 'Only One Punch')),default='Draft')
    sent_to_recipients_count = models.IntegerField(blank=True, default=0)

    attach_offer = models.BooleanField(default=False)
    offer_title = models.CharField(max_length=255, blank=True, null=True)
    offer_expiration = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
	    return self.subject
	
    def get_absolute_url(self):
	    return reverse('message_edit', args=[self.id])
	

	
#Feedback models
class Feedback(models.Model):
    store = models.ForeignKey(Store)
    date_added = models.DateTimeField(auto_now_add=True)
    patron = models.ForeignKey(Patron)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True)
    is_response = models.BooleanField(default=False)
    status = models.IntegerField(max_length=255,choices=((0,'Unread'),(1,'Read')),default=0)

    def get_absolute_url(self):
	    # the details are based on the parent (main) message
	    if self.parent == None:
		    return reverse('feedback_details', args=[self.id])
	    return reverse('feedback_details', args=[self.parent_id])

    def thread_count(self):
	    return Feedback.objects.filter(parent_id=self.id).count()
	
	
