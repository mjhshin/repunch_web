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
    
    modified = models.BooleanField(default=False)
    
    
    class Meta:
        unique_together = (("session_key", "timestamp", "uid"),)
        
class CometSessionIndex(models.Model):
    """
    This is used as a supplement to CometSession- session_keys are 
    the primary keys here!
    
    The purpose of this is to retain the session_key even if the user
    does not have an active tab or window so that comet receive will
    still be able to push notifications in for the session. Remember
    that CometSession will always have a request that it is associated
    with otherwise it will get deleted after a certain time.
    """
    session_key = models.CharField(primary_key=True, max_length=70)
    store_id = models.CharField(max_length=20)
    last_updated = models.DateTimeField()
    
