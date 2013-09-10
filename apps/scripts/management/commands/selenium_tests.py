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
from tests.test_analysis import test_trends, test_breakdown,\
test_reward_redemptions
from tests.test_messages import test_messages, test_feedbacks
from tests.test_employees import test_employees, test_employee_access
from tests.test_settings import test_settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        results = []
        
        ####### PUBLIC #########################################
        results.extend(test_public_pages())
        #results.extend(test_signup())
        #results.extend(test_login_dialog())
        #results.extend(test_login_page())
        
        ####### DASHBOARD #########################################
        #### MY ACCOUNT
        #results.extend(test_edit_store_details()) # TODO added 2 more here
        #results.extend(test_edit_account())
        #results.extend(test_cancel_account())
        
        ### REWARDS
        #results.extend(test_rewards())
        
        ### ANALYSIS
        #results.extend(test_trends()) todo
        #results.extend(test_breakdown()) todo
        #results.extend(test_reward_redemptions()) todo 
        
        ### MESSAGES
        #results.extend(test_messages())
        #results.extend(test_feedbacks())
        
        ### EMPLOYEE
        #results.extend(test_employees())
        #results.extend(test_employee_access()) # TODO FINISH
        
        ### SETTINGS
        #results.extend(test_settings())
        
        ### WORKBENCH
        #results.extend(test_punch()) TODO 
        #results.extend(test_redemptions()) TODO 
        
        
        send_email_selenium_test_results(results)
