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
    "email": "kjsdhgjksh@repunch.com",
}

def test_signup():
    # TODO test place order!
    print "\ntest_signup:"
    print "--------------"   
    
    test = SeleniumTest("SIGNUP", [
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
        {'test_name': "password must be at least 6 characters"},
        {'test_name': "password and corfirmation must be the same"},
    ])

    ##########  Sign up page navigable
    def test_0():
        test.open(reverse("public_signup")) 
        return test.is_current_url(reverse("public_signup"))
    
    test.testit(test_0)
    sleep(1)
    
    ##########  Form submission okay
    def test_1():
        selectors = (
            ("#categories", "baker"),
            ("", Keys.ARROW_DOWN),
            ("", Keys.RETURN),
            ("#categories", "fitn"),
            ("", Keys.ARROW_DOWN),
            ("", Keys.RETURN),
        )
        test.action_chain(1, selectors, action="send_keys") 
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
        test.action_chain(0, selectors, action="send_keys") 
        # ToS and submit
        selectors = (
            "#id_recurring",
            "#signup-form-submit",
        )
        test.action_chain(0, selectors) 
        return True
        
    test.testit(test_1)
        
    ##########  Popup dialog functional
    def test_2():
        # max_wait_time is large because of stupid localhost
        max_wait_time, time_waited = 100, 0
        # the orange clock that pops up after signing up.
        time_img = test.find("#signing-up-time")
        while not time_img.is_displayed() and\
            time_waited < max_wait_time:
            sleep(5)
            time_waited += 5
        return time_waited <= max_wait_time
    
    test.testit(test_2)
    
    user = Account.objects().get(username=TEST_USER['email'],
        include="Store.Subscription,Store.Settings")
            
    ##########  User object created
    def test_3():
        return user is not None
        
    test.testit(test_3)
        
    if user is not None:
        store = user.get("store")
        subscription = store.get("subscription")
        settings = store.get("settings")
        
        ##########  Store object created
        def test_4():
            return store is not None
        ##########  Subscription object created
        def test_5():
            return subscription is not None
        ##########  Settings object created
        def test_6():
            return settings is not None
            
        for i in range(4, 7):
            test.testit(locals()["test_%s" % (str(i),)])
            
        if SeleniumTest.CHECK_SENT_MAIL:
            mail = Mail()
        
        ##########  Email about new user sent to staff
        def test_7():
            if SeleniumTest.CHECK_SENT_MAIL:
                sleep(5) # wait for the email to register in gmail
                return mail.is_mail_sent(\
                        EMAIL_SIGNUP_SUBJECT_PREFIX + store.store_name)
            else:
                return (True, "Test skipped.")
                
        ##########  Welcome email sent to user
        def test_8():
            if SeleniumTest.CHECK_SENT_MAIL:
                return mail.is_mail_sent(\
                    EMAIL_SIGNUP_WELCOME_SUBJECT_PREFIX +
                    store.get_owner_fullname())
            else:
                return (True, "Test skipped.")
        
        ##########  Email must be unique
        def test_9():
            test.open(reverse("public_signup")) 
            test.find("#id_email").send_keys(TEST_USER['email'])
            test.find("#signup-form-submit").click() 
            sleep(3)
            return str(test.find("#email_e ul li").text) ==\
                    "Email is already being used."
    
        for i in range(7, 10):
            test.testit(locals()["test_%s" % (str(i),)])
    
        if SeleniumTest.CHECK_SENT_MAIL:
            mail.logout()
            
        try:
            user.delete()
            store.delete()
            subscription.delete()
            settings.delete()
        except Exception:
            pass
        
    ## Required fields are required!
    test.open(reverse("public_signup")) 
    sleep(1)
    selectors = (
        "#id_store_name",
        "#id_street",
        "#id_city",
        "#id_state",
        "#id_zip",
        "#id_first_name",
        "#id_last_name",
        "#Ph1",
        "#Ph2",
        "#Ph3",
        "#id_email",
        "#id_password",
        "#id_confirm_password",
    )
    test.action_chain(0, selectors, action="clear") 
    test.find("#signup-form-submit").click() 
    sleep(3)
    
    
    ##########  Store name is required
    ##########  Street is required
    ##########  City is required
    ##########  State is required 
    ##########  Zip is required 
    ##########  First name is required 
    ##########  Last name is required 
    ##########  Phone number is required 
    ##########  Email is required 
    ##########  Password is required 
    ##########  Password confirmation is required
    test.fields_required((
        "#store_name_e ul li",
        "#street_e ul li",
        "#city_e ul li",
        "#state_e ul li",
        "#zip_e ul li",
        "#first_name_e ul li",
        "#last_name_e ul li",
        "#phone_number_e ul li",
        "#email_e ul li",
        "#password_e ul li",
        "#password2_e ul li",
    ), test_offset=10)
            
    ##########  ToS is required 
    def test_21():
        return str(test.find("#recurring_e ul li").text) ==\
                "You must accept the Terms & Conditions to continue."
                
    ##########  Invalid address is detected (no coordinates)
    def test_22():
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
        test.find("#signup-form-submit").click() 
        sleep(2)
        return str(test.find("#street_e ul li").text) ==\
            "Enter a valid adress, city, state, and/or zip."
    
    ##########  password must be at least 6 characters
    def test_23():
        # pass1
        pass1 = test.find("#id_password")
        pass1.clear()
        pass1.send_keys("12345")
        test.find("#signup-form-submit").click()
        sleep(2)
        return str(test.find("#password_e ul li").text).__contains__(\
            "Ensure this value has at least 6 characters ")
            
    ##########  password and corfirmation must be the same
    def test_24():
        # pass1
        pass1 = test.find("#id_password")
        pass1.clear()
        pass1.send_keys("1234567")
        # pass2
        pass2 = test.find("#id_confirm_password")
        pass2.clear()
        pass2.send_keys("1234467")
        test.find("#signup-form-submit").click() 
        sleep(2)
        return str(test.find("#password_e ul li").text) ==\
            "Passwords don't match."
            
    for i in range(21, 25):
        test.testit(locals()["test_%s" % (str(i),)])
    

    # END OF ALL TESTS
    return test.tear_down()
