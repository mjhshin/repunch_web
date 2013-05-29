from django.db import models
from django.core.urlresolvers import reverse

from apps.stores.models import Store
from apps.patrons.models import Patron

class Reward(models.Model):
	store = models.ForeignKey(Store)
	reward_name = models.CharField(max_length=255)
	description = models.TextField()
	punches = models.IntegerField()
	reward_avatar = models.ImageField(max_length=255,upload_to='images/avatars/rewards',blank=True,null=True)
	
	def __unicode__(self):
		return self.reward_name	
	
	def delete(self):
		#we need to take care of deleting this file
		if self.reward_avatar:
			self.reward_avatar.delete(save=False)
		
		super(Reward, self).delete()
		
	def get_absolute_url(self):
		return reverse('reward_edit', args=[self.id])
	
	def redemption_count(self):
		return Redemption.objects.filter(reward=self).count()
	
class Punch(models.Model):
	reward = models.ForeignKey(Reward)
	patron = models.ForeignKey(Patron)
	date_punched = models.DateTimeField(auto_now_add=True)
	punches = models.IntegerField(default=0)
	employee = models.ForeignKey("employees.Employee", blank=True, null=True)
	
class Redemption(models.Model):
	reward = models.ForeignKey(Reward)
	patron = models.ForeignKey(Patron)
	date_punched = models.DateTimeField(auto_now_add=True)
	punches = models.IntegerField(default=0)
	employee = models.ForeignKey("employees.Employee", blank=True, null=True)
	
	
