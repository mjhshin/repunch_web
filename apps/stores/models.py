from django.db import models

from libs.repunch import rpforms
from repunch.settings import TIME_ZONE

class Store(models.Model):
	store_name = models.CharField(max_length=255)
	street = models.CharField(max_length=255)
	city = models.CharField(max_length=255)
	state = models.CharField(max_length=255)
	zip = models.CharField(max_length=255)
	country = models.CharField(max_length=255)
	phone_number = models.CharField(max_length=255)
	email = models.EmailField(max_length=255)
	store_description = models.TextField()
	store_avatar = models.ImageField(max_length=255,upload_to='images/avatars/stores',blank=True)
	active_users = models.IntegerField(default=0)
	
	store_timezone = models.CharField(max_length=100,
                        default=TIME_ZONE)
	
	def __unicode__(self):
		return self.store_name
	
	
	def delete(self):
		#we need to take care of deleting this file
		if self.store_avatar:
			self.store_avatar.delete(save=False)
		
		super(Store, self).delete()
	
DAYS = ((1, 'Sunday'),
		(2, 'Monday'),
        (3, 'Tuesday'),
        (4, 'Wednesday'),
        (5, 'Thursday'),
        (6, 'Friday'),
        (7, 'Saturday'))

SHORT_DAYS = ((1, 'Sun'),
		(2, 'Mon'),
        (3, 'Tues'),
        (4, 'Wed'),
        (5, 'Thurs'),
        (6, 'Fri'),
        (7, 'Sat'))

class Hours(models.Model):	
	store = models.ForeignKey(Store)
	days = rpforms.MultiSelectField(max_length=250, blank=True, choices=DAYS)
	open = models.TimeField()
	close = models.TimeField()
	list_order = models.IntegerField(default=0)
	
	class Meta:
		ordering = ['list_order',]
