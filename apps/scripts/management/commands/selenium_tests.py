"""
Run all selenium tests and send the results to ADMIN
"""

from django.core.management.base import BaseCommand

from parse.notifications import send_email_selenium_test_results
from tests.test_public_pages import test_public_pages
from tests.test_signup import test_signup
from tests.test_login_logout import test_login_dialog, test_login_page
from tests.test_myaccount import test_edit_store_details,\
test_edit_account, test_cancel_account
from tests.test_rewards import test_rewards
from tests.test_messages import test_messages, test_feedbacks
from tests.test_employees import test_employees
from tests.test_settings import test_settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        results = []
        
        ####### PUBLIC
        
        # public pages
        #results.extend(test_public_pages())
        # signup
        #results.extend(test_signup())
        # login (dialog)
        #results.extend(test_login_dialog())
        # login (dedicated page)
        #results.extend(test_login_page())
        
        ####### DASHBOARD
        
        #### MY ACCOUNT
        ## edit store details
        #results.extend(test_edit_store_details())
        ## edit account/subscription
        #results.extend(test_edit_account())
        ## cancel account
        #results.extend(test_cancel_account())
        
        ### REWARDS
        #results.extend(test_rewards())
        
        ### MESSAGES
        ## messages
        #results.extend(test_messages())
        ## feedback
        #results.extend(test_feedbacks()) TODO
        
        ### EMPLOYEE
        #results.extend(test_employees()) TODO
        
        ### SETTINGS
        #results.extend(test_settings())
        
        
        
        
        
        send_email_selenium_test_results(results)
