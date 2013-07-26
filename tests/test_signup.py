"""
Selenium test for signup
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest

def test_signup():
    test = SeleniumTest()
    parts = [
        {'test_name': "Sign up page navigable"},
        {'test_name': "Form submission"},
        {'test_name': "User object created"},
        {'test_name': "Store object created"},
        {'test_name': "Subscription object created"},
        {'test_name': "Settings object created"},
    ]
    section = {
        "section_name": "Sign up working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    # wrap the enire thing in a try so that the test results are sent
    try:
        test.open(reverse("public_signup")) # ACTION!
        parts[0]['success'] = True
        sleep(1)
        
        selectors = (
            ("#id_store_name", "test business"),
            ("#id_street", "1370 virginia ave 4d"),
            ("#id_city", "bronx"),
            ("#id_state", "ny"),
            ("#id_zip", "10462"),
            ("#categories", "baker"),
            ("", Keys.ARROW_DOWN),
            ("", Keys.RETURN),
            ("#categories", "fitn"),
            ("", Keys.ARROW_DOWN),
            ("", Keys.RETURN),
            ("#id_first_name", "Testee"),
            ("#id_last_name", "Bestee"),
            ("#Ph1", "777"),
            ("#Ph2", "777"),
            ("#Ph3", "7777"),
            ("#id_email", "test@iusluixylusr.com"),
            ("#id_username", "iusluixylusr"),
            ("#id_password", "iusluixylusr"),
            ("#id_confirm_password", "iusluixylusr"),
        )
        test.action_chain(1, selectors, action="send_keys") # ACTION!
        # ToS and submit
        selectors = (
            "#id_recurring",
            # "#signup-form-submit",
        )
        test.action_chain(2, selectors) # ACTION!
    except Exception:
        pass
    
    # END OF ALL TESTS
    return test.tear_down()
