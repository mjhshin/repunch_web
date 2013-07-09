"""
A simple command that deletes all the rows in CometSession.
"""

from django.core.management.base import BaseCommand

from apps.comet.models import CometSession

class Command(BaseCommand):
    def handle(self, *args, **options):
        CometSession.objects.all().delete()
