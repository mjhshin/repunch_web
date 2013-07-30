"""
Deletes CometSessions that share the same session_key only if it is
not the last object that has that session_key and only if the object
has a timestamp that is older than the REQUEST_TIMEOUT.

These checks are in place so that currently logged in sessions are 
not affected by this script.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from apps.comet.models import CometSession
from repunch.settings import REQUEST_TIMEOUT

class Command(BaseCommand):
    def handle(self, *args, **options):\
        # cache a copy of all the current comets
        comets = CometSession.objects.all()
        now = timezone.now()
        timedout_time = now + relativedelta(seconds=\
            (REQUEST_TIMEOUT+10)*-1)
        for comet in comets:
            # first update the object manager
            CometSession.objects.update()
            
            # 1. check if this is the last object with the session_key
            # 2. only delete if this object has a timestamp that is
            #    older than the REQUEST_TIMEOUT
            if len(CometSession.objects.filter(session_key=\
                comet.session_key) > 1 and\
                comet.datetime < timedout_time:
                comet.delete()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
