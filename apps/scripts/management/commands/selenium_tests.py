"""
Run all selenium tests and send the results to ADMIN
"""

from django.core.management.base import BaseCommand

from tests.test_public_pages import test_public_pages
from tests.test_signup import test_signup
from tests.test_login_logout import test_login_dialog, test_login_page
from tests.test_myaccount import test_edit_store_details
from parse.notifications import send_email_selenium_test_results

class Command(BaseCommand):
    def handle(self, *args, **options):
        results = []
        
        ####### PUBLIC
        
        # PUBLIC PAGES
        # results.extend(test_public_pages())
        # SIGNUP
        results.extend(test_signup())
        # LOGIN (dialog)
        #results.extend(test_login_dialog())
        # LOGIN (dedicated page)
        #results.extend(test_login_page())
        
        ####### DASHBOARD
        # MY ACCOUNT
        # results.extend(test_edit_store_details())
        
        send_email_selenium_test_results(results)