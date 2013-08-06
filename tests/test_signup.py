"""
Selenium test for signup.

I know that this is not how tests are done in Django. 
The justification for this is that we are not using Django Models but
Parse Objects and services so yea.
"""

from django.core.urlresolvers import reverse
from django.utils import timezone
from selenium.webdriver.common.keys import Keys
from time import sleep

from libs.imap import Mail
from libs.dateutil.relativedelta import relativedelta
from tests import SeleniumTest
from parse.apps.accounts.models import Account
from parse.notifications import EMAIL_SIGNUP_SUBJECT_PREFIX

TEST_USER = {
    "username": "iusluixylusr",
    "email": "admin@repunch.com",
}

def test_signup():
    # TODO test place order!
    test = SeleniumTest()
    parts = [
        {'test_name': "Sign up page navigable"},
        {'test_name': "Form submission okay"},
        {'test_name': "Popup dialog functional"},
        {'test_name': "User object created"},
        {'test_name': "Store object created"},
        {'test_name': "Subscription object created"},
        {'test_name': "Settings object created"},
        {'test_name': "Email about new user sent"},
        {'test_name': "Store name is required"},
        {'test_name': "Street is required"},
        {'test_name': "City is required"},
        {'test_name': "State is required"},
        {'test_name': "Zip is required"},
        {'test_name': "First name is required"},
        {'test_name': "Last name is required"},
        {'test_name': "Phone number is required"},
        {'test_name': "Email is required"},
        {'test_name': "Username is required"},
        {'test_name': "Password is required"},
        {'test_name': "ToS check is required"},
        # TODO wrong address
        # TODO username must not contain whitespace
        # TODO password must not contain whitespace
        # TODO password must be at least 6 characters
        # password and corfirmation must be the same
    ]
    section = {
        "section_name": "Sign up working properly?",
        "parts": parts,
    }
    test.results.append(section)

    ##########  Sign up page navigable
    test.open(reverse("public_signup")) # ACTION!
    parts[0]['success'] = True
    sleep(1)
    
    ##########  Form submission okay
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
        ("#id_email", TEST_USER['email']),
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['username']),
        ("#id_confirm_password", TEST_USER['username']),
    )
    try:
        test.action_chain(1, selectors, action="send_keys") # ACTION!
        # ToS and submit
        selectors = (
            "#id_recurring",
            "#signup-form-submit",
        )
        test.action_chain(2, selectors) # ACTION!
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
    else:
        parts[1]['success'] = True
        sleep(1) 
        
    ##########  Popup dialog functional
    max_wait_time, time_waited = 10, 0
    # the orange clock that pops up after signing up.
    try:
        time_img =\
            test.driver.find_element_by_id("signing-up-time")
        while not time_img.is_displayed():
            sleep(1)
            time_waited += 1
        if time_waited < 10:
            parts[2]['success'] = True
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)

    ##########  User object created
    user = Account.objects().get(username=TEST_USER['username'],
        include="Store.Subscription,Store.Settings")
    parts[3]['success'] = user is not None
    ##########  Store object created
    if user is not None:
        store = user.get("store")
        parts[4]['success'] = store is not None
        ##########  Subscription object created
        subscription = store.get("subscription")
        parts[5]['success'] = subscription is not None
        ##########  Settings object created
        settings = store.get("settings")
        parts[6]['success'] = settings is not None
        
    
        ##########  Email about new user sent
        sleep(5) # wait for the email to register in gmail
        mail = Mail()
        mail.select_sent_mailbox()
        mail_ids=mail.search_by_subject(EMAIL_SIGNUP_SUBJECT_PREFIX +\
            store.store_name)
        if len(mail_ids) > 0:
            sent = mail.fetch_date(str(mail_ids[-1]))
            now = timezone.now()
            lb = now + relativedelta(seconds=-10)
            # make sure that this is the email that was just sent
            if now.year == sent.year and now.month == sent.month and\
                now.day == sent.day and now.hour == sent.hour and\
                (sent.minute == now.minute or\
                    sent.minute == lb.minute):
                parts[7]['success'] = True
    
        mail.logout()
        user.delete()
        store.delete()
        subscription.delete()
        settings.delete()
        
    #  Required fields are required!
    test.open(reverse("public_signup")) # ACTION!
    sleep(1)
    selectors = (
        ("#id_store_name", "    "),
        ("#id_street", "   "),
        ("#id_city", "   "),
        ("#id_state", "   "),
        ("#id_zip", "   "),
        ("#id_first_name", "   "),
        ("#id_last_name", " "),
        ("#Ph1", "   "),
        ("#Ph2", "   "),
        ("#Ph3", "    "),
        ("#id_email", "   "),
        ("#id_username", "   "),
        ("#id_password", "         "),
        ("#id_confirm_password", "         "),
    )
    test.action_chain(0, selectors, action="send_keys") # ACTION!
    # submit
    test.find("#signup-form-submit").click() # ACTION!
    sleep(3)
    
    ##########  Store name is required
    parts[8]['success'] =\
        str(test.find("//p[@id='store_info']/ul[1]/li", 
            type="xpath").text) == "This field is required."
    ##########  Street is required
    parts[9]['success'] =\
        str(test.find("//p[@id='store_info']/ul[2]/li", 
            type="xpath").text) == "This field is required."
    ##########  City is required
    parts[10]['success'] =\
        str(test.find("//p[@id='store_info']/" +\
            "div[@class='floated'][1]/ul/li", 
            type="xpath").text) == "This field is required."
    ##########  State is required 
    parts[11]['success'] =\
        str(test.find("//p[@id='store_info']/" +\
            "div[@class='floated'][2]/ul/li", 
            type="xpath").text) == "This field is required."
    ##########  Zip is required 
    parts[12]['success'] =\
        str(test.find("//p[@id='store_info']/" +\
            "div[@class='floated'][3]/ul/li", 
            type="xpath").text) == "This field is required."
    ##########  First name is required 
    parts[13]['success'] =\
        str(test.find("//p[@id='account_info']/" +\
            "div[@class='floated'][1]/ul/li", 
            type="xpath").text) == "This field is required."
    ##########  Last name is required 
    parts[14]['success'] =\
        str(test.find("//p[@id='account_info']/" +\
            "div[@class='floated'][2]/ul/li", 
            type="xpath").text) == "This field is required."
    ##########  Phone number is required 
    parts[15]['success'] =\
        str(test.find("//p[@id='account_info']/ul[1]/li", 
            type="xpath").text) == "Enter a valid phone number."
    ##########  Email is required 
    parts[16]['success'] =\
        str(test.find("//p[@id='account_info']/ul[2]/li", 
            type="xpath").text) == "This field is required."
    ##########  Username is required
    parts[17]['success'] =\
        str(test.find("//p[@id='account_info']/ul[3]/li[1]", 
            type="xpath").text) == "This field is required." and\
        str(test.find("//p[@id='account_info']/ul[3]/li[2]", 
            type="xpath").text) == "Must contain only alpha-numeric" +\
            " characters without spaces."
    ##########  Password is required 
    parts[18]['success'] =\
        str(test.find("//p[@id='account_info']/ul[4]/li[1]", 
            type="xpath").text) == "This field is required." and\
        str(test.find("//p[@id='account_info']/ul[4]/li[2]", 
            type="xpath").text) == "Must contain only alpha-numeric" +\
            " characters without spaces."
    ##########  ToS is required 
    parts[19]['success'] =\
        str(test.find("//div[@id='recurring_charge_container']/ul/li", 
            type="xpath").text) == "You must accept the Terms" +\
                " & Conditions to continue."
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()
