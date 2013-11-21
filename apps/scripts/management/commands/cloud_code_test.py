"""
Run all cloud code tests and send the results to ADMIN
"""

from django.core.management.base import BaseCommand

from parse.notifications import send_email_cloud_test_results
from cloud_code.tests.test_add_delete_patronstore import\
test_add_delete_patronstore

class Command(BaseCommand):
    def handle(self, *args, **options):
        results = []
        
        for i in range(100):
            results.extend(test_add_delete_patronstore()) 
        
        send_email_cloud_test_results(results)
