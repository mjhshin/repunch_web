from django.db import models 

class Category(models.Model):
    """ store static data for fast querying """
    alias = models.CharField(max_length=100, default='',
                                primary_key=True)
    name = models.CharField(max_length=100, unique=True,
                        default='')

    
