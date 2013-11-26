"""
Run all cloud code tests and send the results to ADMIN
"""

from django.core.management.base import BaseCommand

from parse.notifications import send_email_cloud_test_results
from cloud_code.tests.test_add_delete_patronstore import\
TestAddDeletePatronStore
from cloud_code.tests.test_punch import TestPunch
#from cloud_code.tests.test_request_validate_reject_redeem import\
#TestRequestValidateRejectRedeem

class Command(BaseCommand):
    def handle(self, *args, **options):
        results = []
        
        #results.extend(TestAddDeletePatronStore().get_results()) 
        results.extend(TestPunch().get_results())
        #results.extend(TestRequestValidateRejectRedeem.get_results())
        
        if "dryrun" not in args:
            send_email_cloud_test_results(results)
