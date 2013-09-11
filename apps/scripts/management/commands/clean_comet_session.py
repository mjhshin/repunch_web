"""
Deletes CometSessionIndexes (and related CometSessions) 
if it was last updated more than 24 hours. Why 24 hours? 
Remember that there is a stay signed in option that may conflict with
the user clearing the browser data whilst still logged in, 
which results in a dangling session_key. Also, if the user does not
choose to stay signed in, then we still get a dangling session_key.

These checks are in place so that currently logged in sessions are 
not affected by this script.

If force, all sessions are flushed and all CometSessions are set to
modified in order to force another pull from comet.js and immediately
log users out due to the login_required decorator in comet pull view.
The comet objects are then deleted after COMET_PULL_RATE to kill any
threads still running in the server.
"""

from django.core.management.base import BaseCommand
from django.contrib.sessions.backends.cache import SessionStore
from django.utils import timezone
from time import sleep

from libs.dateutil.relativedelta import relativedelta
from apps.comet.models import CometSession, CometSessionIndex
from parse.utils import flush
from repunch.settings import COMET_PULL_RATE

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
            
        to_del = []
        
        for cometi in  CometSessionIndex.objects.all():
            if cometi.last_updated < timedout_time or force:
                session = SessionStore(cometi.session_key)
                flush(session)
                to_del.append(cometi)
                # delete associated cometsessions 
                for comet in CometSession.objects.filter(\
                    session_key=cometi.session_key):
                    to_del.append(comet)    
                    if force:
                         comet.modified = True
                         comet.save()
       
        # wait for the threads in the server to detect modified
        if force:
            sleep(COMET_PULL_RATE + 3)
            
        # now actually delete the objects
        for c in to_del:
            c.delete()
            
        # check for dangling cometsessions that did not get terminated
        for comet in CometSession.objects.all():
            # delete if no associated cometsessionindex exists
            cs = CometSession.objects.filter(\
                session_key=comet.session_key)
            for c in cs:
                c.delete()
      
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
