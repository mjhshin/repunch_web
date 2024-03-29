from django.db import models 

class Category(models.Model):
    """ store static data for fast querying """
    name = models.CharField(max_length=100, unique=True,
                        default='')
    # multiple names may have same aliases
    alias = models.CharField(max_length=100, default='')

    def __unicode__(self):
        return self.name
    
