from django.db import models

from libs.repunch import rpforms
from repunch.settings import TIME_ZONE, MEDIA_ROOT
from parse.utils import delete_file
	
class StoreActivate(models.Model):
	store_id = models.CharField(max_length=30)
	
class UploadedAndCreatedImageFile(models.Model):
    """ 
    Used when creating a new StoreLocation and the user decides to
    crop an image for a non-existent ParseObject.
    """
    session_key = models.CharField(max_length=100)
    image_name = models.TextField()
    image_url = models.TextField()
    
    def delete(self, delete_from_parse=False):
        if delete_from_parse:
            delete_file(self.image_name, 'image/png') 
                  
        super(UploadedImageFile, self).delete()

class UploadedImageFile(models.Model):
    """ 
    This is used in the image upload sequence. The file needs to be 
    uploaded first so that the user may crop the image and finally
    create the parse file.
    
    Might need to clean this every now and then because it is not 
    guaranteed that a user will crop what they upload before logging out.
    """
    session_key = models.CharField(max_length=100)
    image = models.ImageField(upload_to='tmp/images/avatars')
    
    def delete(self):
        try:
            self.image.delete()
        except Exception:
            pass
       
        super(UploadedImageFile, self).delete()

class Store(models.Model):
    store_name = models.CharField(max_length=255, 
                            default="fake", blank=True)
    store_description = models.TextField(blank=True, default="")

    store_timezone = models.CharField(max_length=100,
                        default=TIME_ZONE, blank=True)

    def __unicode__(self):
	    return self.store_name
	
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
    store = models.ForeignKey(Store, blank=True, null=True)
    days = rpforms.MultiSelectField(max_length=250, blank=True, 
                            choices=DAYS)
    open = models.TimeField()
    close = models.TimeField()
    list_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['list_order',]
