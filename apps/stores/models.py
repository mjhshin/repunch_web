from django.db import models

from libs.repunch import rpforms
from repunch.settings import TIME_ZONE, MEDIA_ROOT

	
class StoreActivate(models.Model):
	store_id = models.CharField(max_length=30)

class StoreLocationAvatarTmp(models.Model):
    """ 
    This is used in the image upload sequence. The file needs to be 
    uploaded first so that the user may crop the image and finally
    create the parse file.
    
    Need to clean this out every night!
    for each in StoreLocationAvatarTmp.objects.all():
        each.avatar.delete()
        each.delete()
    """
    session_key = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='tmp/images/avatars')
    
    def delete(self):
        try:
            avatar.delete()
        except Exception:
            pass

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
