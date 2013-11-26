"""
Run all selenium tests and send the results to ADMIN
"""

from django.core.management.base import BaseCommand

from parse.notifications import send_email_selenium_test_results
from tests.test_public_pages import TestPublicPages
#from tests.test_signup import TestSignUp
#from tests.test_login_logout import TestLoginDialog, TestLoginPage
#from tests.test_mystore import TestEditStoreDetails,\
#TestUpdateSubscription, TestCancelAccount
#from tests.test_rewards import TestRewards
#from tests.test_analysis import TestTrends, TestBreakdown,\
#TestRewardRedemptions
#from tests.test_messages import TestMessages, TestFeedbacks
#from tests.test_employees import TestEmployees, TestEmployeeAccess,\
#TestEmployeeRegistration
#from tests.test_settings import TestSettings
#from tests.test_workbench import TestPunch, TestRedemptions

class Command(BaseCommand):
    def handle(self, *args, **options):
        dryrun = "dryrun" in args
        verbose = "verbose" in args
    
        results = (
            ####### PUBLIC #########################################
            TestPublicPages().get_results(verbose),
            #TestSignUp().get_results(verbose),
            #TestLoginDialog().get_results(verbose),
            #TestLoginPage().get_results(verbose),
            
            ####### DASHBOARD #########################################
            #### MY STORE
            #TestEditStoreDetails().get_results(verbose),
            #TestUpdateSubscription().get_results(verbose),
            #TestCancelAccount().get_results(verbose),
            
            ### REWARDS
            #TestRewards().get_results(verbose),
            
            ### ANALYSIS
            #TestTrends().get_results(verbose), todo?
            #TestBreakdown().get_results(verbose), todo?
            #TestRewardRedemptions().get_results(verboes), todo?
            
            ### MESSAGES
            #TestMessages().get_results(verbose),
            #TestFeedbacks().get_results(verbose),
            
            ### EMPLOYEE
            #TestEmployees().get_results(verbose),
            #TestEmployeeAccess().get_results(verbose),
            #TestEmployeeRegistration().get_results(verbose),
            
            ### SETTINGS
            #TestSettings().get_results(verbose),
            
            ### WORKBENCH
            #TestPunch().get_results(verbose),
            #TestRedemptions().get_results(verbose), # TODO finish
            
            ### ACCOUNT SETTINGS
            #TestAccountSettings().get_results(verbose), # TODO
        )
        
        if not dryrun:
            send_email_selenium_test_results(results)
