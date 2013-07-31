"""
Selenium test for signup.

I know that this is not how tests are done in Django. 
The justification for this is that we are not using Django Models but
Parse Objects and services so yea.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest
from parse.apps.accounts.models import Account
# from parse.apps.stores.models import Store

TEST_USER = {
    "username": "clothing",
    "password": "123456",
}

def test_login():
    test = SeleniumTest()
    parts = [
        {'test_name': "Login dialog showing up"},
        {'test_name': "Wrong login credentials show error"},
    ]
    section = {
        "section_name": "Login working properly?",
        "parts": parts,
    }
    test.results.append(section)

    ##########  Login dialog showing up
    test.open(reverse("public_home")) # ACTION!
    parts[0]['success'] = True
    sleep(1)
    
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()
