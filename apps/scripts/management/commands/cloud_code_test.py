"""
Run all cloud code tests and send the results to ADMIN
"""

from django.core.management.base import BaseCommand

from parse.notifications import send_email_selenium_test_results
from cloud_coud.tests.test_add_delete_patron_store import\
test_add_delete_patron_store

class Command(BaseCommand):
    def handle(self, *args, **options):
        results = []
        
        results.extend(test_add_delete_patron_store()) 
        
        send_email_selenium_test_results(results)
