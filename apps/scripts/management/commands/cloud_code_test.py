"""
Run all cloud code tests and send the results to ADMIN
"""

from django.core.management.base import BaseCommand

from parse.notifications import send_email_cloud_test_results
from cloud_code.tests.test_add_delete_patronstore import\
TestAddDeletePatronStore
from cloud_code.tests.test_punch import TestPunch
from cloud_code.tests.test_request_validate_reject_redeem import\
TestRequestValidateRejectRedeem

class Command(BaseCommand):
    def handle(self, *args, **options):
        dryrun = "dryrun" in args
        verbose = "verbose" in args
    
        results = (
            TestAddDeletePatronStore().get_results(verbose),
            TestPunch().get_results(verbose),
            TestRequestValidateRejectRedeem().get_results(verbose),
        )
        
        if not dryrun:
            send_email_cloud_test_results(results)
