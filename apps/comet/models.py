from django.db import models

class CometSession(models.Model):
    """
    Associates a session ID with a boolean used to flag a request
    to call the cloud code retailer_refresh to go through.
    
    Note that there may be multiple dashboards open for the same store
    so we cannot just use the store_id as a unique identifier.
    """
    # this is the request.session.session_key!
    session_key = models.CharField(max_length=70, primary_key=True)
    store_id = models.CharField(max_length=20)
    modified = models.BooleanField(default=False)
