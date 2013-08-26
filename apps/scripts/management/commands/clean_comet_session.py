"""
Deletes CometSessionIndexes (and related CometSessions) 
if it was last updated more than 24 hours. Why 24 hours? 
Remember that there is a stay signed in option that may conflict with
the user clearing the browser data whilst still logged in, 
which results in a dangling session_key. Also, if the user does not
choose to stay signed in, then we still get a dangling session_key.

These checks are in place so that currently logged in sessions are 
not affected by this script.

This script may also be used to force log out all users.
"""

from django.core.management.base import BaseCommand
from django.contrib.sessions.backends.cache import SessionStore
from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from apps.comet.models import CometSession, CometSessionIndex

LAST_UPDATED_THRESHOLD = 24 # in hours

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        posible values in args:
            - force : terminate ALL sessions - even active ones
        """
        force = "force" in args
    
        now = timezone.now()
        timedout_time = now + relativedelta(hours=\
            -1*LAST_UPDATED_THRESHOLD)
        # cache a copy of all the current comet indicies
        cometis = CometSessionIndex.objects.all()
        
        # its important to cache the cometsession here as well to
        # avoid gaps
        comets = CometSession.objects.all()
        
        for cometi in cometis:
            if cometi.last_updated < timedout_time or force:
                session = SessionStore(cometi.session_key)
                session.flush()
                cometi.delete()
                # also delete associated cometsessions 
                # (there shouldn't be any at all though)
                for comet in CometSessionIndex.objects.filter(\
                    session_key=cometi.session_key):
                    comet.delete()
            
        # check for dangling cometsessions that did not get terminated
        for comet in comets:
            # delete if no associated cometsessionindex exists
            cs = CometSession.objects.filter(\
                session_key=comet.session_key)
            for c in cs:
                c.delete()
      
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
