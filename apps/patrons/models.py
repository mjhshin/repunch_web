from django.db import models
from apps.stores.models import Store

class Patron(models.Model):
    stores = models.ManyToManyField(Store, through='PatronStore')
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    gender = models.IntegerField(choices=((0,'Unknown'),(1,'Male'),(2, 'Female')),default=0)
    dob = models.DateField(null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)
    status = models.IntegerField(choices=((0,'Inactive'),(1,'Active')),default=0)
        
        
class PatronStore(models.Model):
    patron = models.ForeignKey(Patron)
    store = models.ForeignKey(Store)
    date_added = models.DateField(auto_now_add=True)
    
    
class FacebookPost(models.Model):
    patron = models.ForeignKey(Patron)
    store = models.ForeignKey(Store)
    date_posted = models.DateField(auto_now_add=True)