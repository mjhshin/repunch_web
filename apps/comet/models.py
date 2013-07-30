from django.db import models

class CometSession(models.Model):
    """
    Note that there may be multiple dashboards open for the same store
    so we cannot just use the store_id as a unique identifier.
    """
    # this is the request.session.session_key!
    session_key = models.CharField(max_length=70)
    # hours:minutes:seconds e.g. 08:07:21
    timestamp = models.CharField(max_length=8)
    # number from 0 to 998
    uid = models.CharField(max_length=3)
    
    # this equates to the same time as timestamp but has date info
    datetime = models.DateTimeField()
    
    store_id = models.CharField(max_length=20)
    modified = models.BooleanField(default=False)
    
    
    class Meta:
        unique_together = (("session_key", "timestamp", "uid"),)
