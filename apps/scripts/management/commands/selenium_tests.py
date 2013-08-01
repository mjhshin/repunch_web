"""
Run all selenium tests and send the results to ADMIN
"""

from django.core.management.base import BaseCommand

from tests.test_public_pages import test_public_pages
from tests.test_signup import test_signup
from tests.test_login import test_login_dialog#, test_login_page
from parse.notifications import send_email_selenium_test_results

class Command(BaseCommand):
    def handle(self, *args, **options):
        results = []
        
        # PUBLIC PAGES
        # results.extend(test_public_pages())
        # SIGNUP
        # results.extend(test_signup())
        # LOGIN
        results.extend(test_login_dialog())
        
        send_email_selenium_test_results(results)
