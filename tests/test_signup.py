"""
Selenium test for signup.

I know that this is not how tests are done in Django. 
The justification for this is that we are not using Django Models but
Parse Objects and services so yea.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from libs.imap import Mail
from tests import SeleniumTest
from parse.apps.accounts.models import Account
from parse.notifications import EMAIL_SIGNUP_SUBJECT_PREFIX,\
EMAIL_SIGNUP_WELCOME_SUBJECT_PREFIX

TEST_USER = {
    "email": "vanman00@kayk.com",
}

def test_signup():
    # TODO test place order!
    test = SeleniumTest()
    parts = [
        {'test_name': "Sign up page navigable"},
        {'test_name': "Form submission okay"},
        {'test_name': "Popup dialog functional"},
        {'test_name': "User object created & email used as username"},
        {'test_name': "Store object created"},
        {'test_name': "Subscription object created"},
        {'test_name': "Settings object created"},
        {'test_name': "Email about new user sent to staff"},
        {'test_name': "Welcome email sent to user"}, 
        {'test_name': "Email must be unique"},
        {'test_name': "Store name is required"},
        {'test_name': "Street is required"},
        {'test_name': "City is required"},
        {'test_name': "State is required"},
        {'test_name': "Zip is required"},
        {'test_name': "First name is required"},
        {'test_name': "Last name is required"},
        {'test_name': "Phone number is required"},
        {'test_name': "Email is required"},
        {'test_name': "Password is required"},
        {'test_name': "Password confirmation is required"},
        {'test_name': "ToS check is required"},
        {'test_name': "Invalid address is detected (no coordinates)"},
        {'test_name': "password must not contain whitespace"},
        {'test_name': "password must be at least 6 characters"},
        {'test_name': "password and corfirmation must be the same"},
        
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
    try:
        selectors = (
            ("#categories", "baker"),
            ("", Keys.ARROW_DOWN),
            ("", Keys.RETURN),
            ("#categories", "fitn"),
            ("", Keys.ARROW_DOWN),
            ("", Keys.RETURN),
        )
        test.action_chain(1, selectors, action="send_keys") # ACTION!
        selectors = (
            ("#id_store_name", "test business"),
            ("#id_street", "1370 virginia ave 4d"),
            ("#id_city", "bronx"),
            ("#id_state", "ny"),
            ("#id_zip", "10462"),
            ("#id_first_name", "Testee"),
            ("#id_last_name", "Bestee"),
            ("#Ph1", "777"),
            ("#Ph2", "777"),
            ("#Ph3", "7777"),
            ("#id_email", TEST_USER['email']),
            ("#id_password", 
                TEST_USER['email'].replace("@", "").replace(".", "")),
            ("#id_confirm_password",
                TEST_USER['email'].replace("@", "").replace(".", "")),
        )
        test.action_chain(0, selectors, action="send_keys") # ACTION!
        # ToS and submit
        selectors = (
            "#id_recurring",
            "#signup-form-submit",
        )
        test.action_chain(0, selectors) # ACTION!
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
        while not time_img.is_displayed() and\
            time_waited < max_wait_time:
            sleep(1)
            time_waited += 1
        parts[2]['success'] = time_waited < max_wait_time
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)

    ##########  User object created
    try:
        user = Account.objects().get(username=TEST_USER['email'],
            include="Store.Subscription,Store.Settings")
        parts[3]['success'] = user is not None
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
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
        
        ##########  Email about new user sent to staff
        sleep(5) # wait for the email to register in gmail
        if SeleniumTest.CHECK_SENT_MAIL:
            mail = Mail()
            try:
                parts[7]['success'] = mail.is_mail_sent(\
                    EMAIL_SIGNUP_SUBJECT_PREFIX + store.store_name)
            except Exception as e:
                print e
                parts[7]['test_message'] = str(e)
        else:
            parts[7]['success'] = True
                
        ##########  Welcome email sent to user
        if SeleniumTest.CHECK_SENT_MAIL:
            try:
                parts[8]['success'] = mail.is_mail_sent(\
                    EMAIL_SIGNUP_WELCOME_SUBJECT_PREFIX +
                    store.get_owner_fullname())
            except Exception as e:
                print e
                parts[8]['test_message'] = str(e)
        else:
            parts[8]['success'] = True
        
        test.open(reverse("public_signup")) # ACTION!
        test.find("#id_email").send_keys(TEST_USER['email'])
        # submit
        test.find("#signup-form-submit").click() # ACTION!
        sleep(3)
        ##########  Email must be unique
        try:
            parts[9]['success'] =\
                str(test.find("#email_e ul li").text) ==\
                    "Email is already being used."
        except Exception as e:
            print e
            parts[9]['test_message'] = str(e)
    
        if SeleniumTest.CHECK_SENT_MAIL:
            mail.logout()
            
        user.delete()
        store.delete()
        subscription.delete()
        settings.delete()
        
    ## Required fields are required!
    try:
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
            ("#id_password", "         "),
            ("#id_confirm_password", "         "),
        )
        test.action_chain(0, selectors, action="send_keys") # ACTION!
        # submit
        test.find("#signup-form-submit").click() # ACTION!
        sleep(3)
    except Exception as e:
        print e
    
    ##########  Store name is required
    try:
        parts[10]['success'] =\
            str(test.find("#store_name_e ul li").text) ==\
                "This field is required."
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
    ##########  Street is required
    try:
        parts[11]['success'] =\
            str(test.find("#street_e ul li").text) ==\
                "This field is required."
    except Exception as e:
        print e
        parts[11]['test_message'] = str(e)
    ##########  City is required
    try:
        parts[12]['success'] =\
            str(test.find("#city_e ul li").text) ==\
                "This field is required."
    except Exception as e:
        print e
        parts[12]['test_message'] = str(e)
    ##########  State is required 
    try:
        parts[13]['success'] =\
            str(test.find("#state_e ul li").text) ==\
                "This field is required."
    except Exception as e:
        print e
        parts[13]['test_message'] = str(e)
    ##########  Zip is required 
    try:
        parts[14]['success'] =\
            str(test.find("#zip_e ul li").text) ==\
                "This field is required."
    except Exception as e:
        print e
        parts[14]['test_message'] = str(e)
    ##########  First name is required 
    try:
        parts[15]['success'] =\
            str(test.find("#first_name_e ul li").text) ==\
                "This field is required."
    except Exception as e:
        print e
        parts[15]['test_message'] = str(e)
    ##########  Last name is required 
    try:
        parts[16]['success'] =\
            str(test.find("#last_name_e ul li").text) ==\
                "This field is required."
    except Exception as e:
        print e
        parts[16]['test_message'] = str(e)
    ##########  Phone number is required 
    try:
        parts[17]['success'] =\
            str(test.find("#phone_number_e ul li").text) ==\
                "This field is required."
    except Exception as e:
        print e
        parts[17]['test_message'] = str(e)
    ##########  Email is required 
    try:
        parts[18]['success'] =\
            str(test.find("#email_e ul li").text) ==\
                "This field is required."
    except Exception as e:
        print e
        parts[18]['test_message'] = str(e)
    ##########  Password is required 
    try:
        e1, e2 = test.find("#password_e ul li", multiple=True)
        parts[19]['success'] =\
            str(e1.text) == "This field is required." and\
            str(e2.text) == "Must contain only alpha-numeric" +\
                " characters without spaces."
    except Exception as e:
        print e
        parts[19]['test_message'] = str(e)
    ##########  Password confirmation is required
    try:
        e1, e2 = test.find("#password2_e ul li", multiple=True)
        parts[20]['success'] =\
            str(e1.text) == "This field is required." and\
            str(e2.text) == "Must contain only alpha-numeric" +\
                " characters without spaces."
    except Exception as e:
        print e
        parts[20]['test_message'] = str(e)
    ##########  ToS is required 
    try:
        parts[21]['success'] =\
            str(test.find("#recurring_e ul li").text) ==\
                "You must accept the Terms & Conditions to continue."
    except Exception as e:
        print e
        parts[21]['test_message'] = str(e)
            
    ##########  Invalid address is detected (no coordinates)
    try:
        # street
        street = test.find("#id_street")
        street.clear()
        street.send_keys("988 dsgsd s")
        # city
        city = test.find("#id_city")
        city.clear()
        city.send_keys("mandarin")
        # state
        state = test.find("#id_state")
        state.clear()
        state.send_keys("klk")
        # zip
        zip = test.find("#id_zip")
        zip.clear()
        zip.send_keys("941091")
        # submit
        test.find("#signup-form-submit").click() # ACTION!
        sleep(2)
        parts[22]['success'] =\
            str(test.find("#street_e ul li").text) ==\
            "Enter a valid adress, city, state, and/or zip."
    except Exception as e:
        print e
        parts[22]['test_message'] = str(e)
   
    ## no whitespace
    try:
        # password
        pass2 = test.find("#id_password")
        pass2.clear()
        pass2.send_keys("123 567")
        # submit
        test.find("#signup-form-submit").click() # ACTION!
        sleep(2)
        ##########  password must not contain whitespace
        parts[23]['success'] =\
            str(test.find("#password_e ul li").text) == "Must " +\
            "contain only alpha-numeric characters without spaces."
    except Exception as e:
        print e
        parts[23]['test_message'] = str(e)
    
    ##########  password must be at least 6 characters
    try:
        # pass1
        pass1 = test.find("#id_password")
        pass1.clear()
        pass1.send_keys("12345")
        # pass2
        pass2 = test.find("#id_confirm_password")
        pass2.clear()
        pass2.send_keys("12345")
        # submit
        test.find("#signup-form-submit").click() # ACTION!
        sleep(2)
        parts[24]['success'] =\
            str(test.find("#password_e ul li").text) ==\
            "Ensure this value has at least 6 characters " +\
            "(it has 5)." and str(test.find(\
            "#password2_e ul li").text)== "Ensure this " +\
            "value has at least 6 characters (it has 5)."
    except Exception as e:
        print e
        parts[24]['test_message'] = str(e)
 
    ##########  password and corfirmation must be the same
    try:
        # pass1
        pass1 = test.find("#id_password")
        pass1.clear()
        pass1.send_keys("1234567")
        # pass2
        pass2 = test.find("#id_confirm_password")
        pass2.clear()
        pass2.send_keys("1234467")
        # submit
        test.find("#signup-form-submit").click() # ACTION!
        sleep(2)
        parts[25]['success'] =\
            str(test.find("#password_e ul li").text) ==\
            "Passwords don't match"
    except Exception as e:
        print e
        parts[25]['test_message'] = str(e)
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down()
