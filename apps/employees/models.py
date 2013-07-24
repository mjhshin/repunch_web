from django.db import models
from django.db.models import Sum

from apps.stores.models import Store
from apps.rewards.models import Punch

class Employee(models.Model):
	store = models.ForeignKey(Store)
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	date_added = models.DateField(auto_now_add=True)
	status = models.IntegerField(choices=((0,'pending'),(1,'approved'),(2,'denied')),default=0)
	employee_avatar = models.ImageField(max_length=255,upload_to='images/avatars/employees',blank=True)
	
	def delete(self):
		#we need to take care of deleting this file
		if self.employee_avatar:
			self.employee_avatar.delete(save=False)
			
		#set all employee punches to empty
		
		super(Employee, self).delete()
		
	
	def lifetime_punches(self):
		rv = Punch.objects.filter(employee=self).aggregate(num_punches=Sum('punches'))
		return rv['num_punches']


