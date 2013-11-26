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

class TestSignUp(SeleniumTest):
    # TODO test place order!
    
    USER = { "email" : "17cb6x27833sdhgjk@repunch.com" }
    
    def __init__(self):
        super(TestSignUp, self).__init__(False)
        
        ## Required fields are required!
        def fields_required():
            self.open(reverse("public_signup")) 
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
            self.action_chain(0, selectors, action="clear") 
            self.find("#signup-form-submit").click() 
            sleep(3)
            return True
        
        # tests 10 to 20
        self.fields_required((
            ("#store_name_e ul li", "Store name is required"),
            ("#street_e ul li", "Street is required"),
            ("#city_e ul li", "City is required"),
            ("#state_e ul li", "State is required"),
            ("#zip_e ul li", "Zip is required"),
            ("#first_name_e ul li", "First name is required"),
            ("#last_name_e ul li", "Last name is required"),
            ("#phone_number_e ul li", "Phone number is required"),
            ("#email_e ul li", "Email is required"),
            ("#password_e ul li", "Password is required"),
            ("#password2_e ul li", "Password confirmation is required"),
        ), init_func=fields_required, test_offset=10)

    def test_0(self):
        """
        Sign up page navigable
        """
        self.open(reverse("public_signup")) 
        sleep(2)
        return self.is_current_url(reverse("public_signup"))
    
    def test_1(self):
        """
        Form submission okay
        """
        selectors = (
            ("#categories", "baker"),
            ("", Keys.ARROW_DOWN),
            ("", Keys.RETURN),
            ("#categories", "fitn"),
            ("", Keys.ARROW_DOWN),
            ("", Keys.RETURN),
        )
        self.action_chain(1, selectors, action="send_keys") 
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
            ("#id_email", self.USER['email']),
            ("#id_password", 
                self.USER['email'].replace("@", "").replace(".", "")),
            ("#id_confirm_password",
                self.USER['email'].replace("@", "").replace(".", "")),
        )
        self.action_chain(0, selectors, action="send_keys") 
        # ToS and submit
        selectors = (
            "#id_recurring",
            "#signup-form-submit",
        )
        self.action_chain(0, selectors) 
        return True
        
    def test_2(self):
        """
        Popup dialog functional
        """
        # max_wait_time is large because of stupid localhost
        max_wait_time, time_waited = 100, 0
        # the orange clock that pops up after signing up.
        time_img = self.find("#signing-up-time")
        while not time_img.is_displayed() and\
            time_waited < max_wait_time:
            sleep(5)
            time_waited += 5
        return time_waited <= max_wait_time
    
    def test_3(self):
        """
        User object created
        """
        self.user = Account.objects().get(username=self.USER['email'],
            include="Store.Subscription,Store.Settings")
        return self.user is not None
        
    def test_4(self):
        """
        Store object created
        """
        return self.user.store is not None
        
    def test_5(self):
        """
        Subscription object created
        """
        return self.user.store.subscription is not None
        
    def test_6(self):
        """
        Settings object created
        """
        return self.user.store.settings is not None
        
    def test_7(self):
        """
        Email about new user sent to staff
        """
        if self.CHECK_SENT_MAIL:
            self.mail = Mail()
            sleep(5) # wait for the email to register in gmail
            return self.mail.is_mail_sent(\
                    EMAIL_SIGNUP_SUBJECT_PREFIX +\
                    self.user.store.store_name)
        else:
            return (True, "Test skipped.")
        
    def test_8(self):
        """
        Welcome email sent to user
        """
        if self.CHECK_SENT_MAIL:
            return self.mail.is_mail_sent(\
                EMAIL_SIGNUP_WELCOME_SUBJECT_PREFIX +
                self.user.store.get_owner_fullname())
        else:
            return (True, "Test skipped.")
    
    def test_9(self):
        """
        Email must be unique
        """
        self.open(reverse("public_signup")) 
        self.find("#id_email").send_keys(self.USER['email'])
        self.find("#signup-form-submit").click() 
        
        sleep(3)
        if self.CHECK_SENT_MAIL:
            self.mail.logout()
        self.user.delete()
        self.user.store.delete()
        self.user.store.subscription.delete()
        self.user.store.settings.delete()
        
        return self.find("#email_e ul li").text ==\
                "Email is already being used."
                
    def test_21(self):
        """
        ToS is required 
        """
        return str(self.find("#recurring_e ul li").text) ==\
                "You must accept the Terms & Conditions to continue."
                
    def test_22(self):
        """
        Invalid address is detected (no coordinates)
        """
        # street
        street = self.find("#id_street")
        street.clear()
        street.send_keys("988 dsgsd s")
        # city
        city = self.find("#id_city")
        city.clear()
        city.send_keys("mandarin")
        # state
        state = self.find("#id_state")
        state.clear()
        state.send_keys("klk")
        # zip
        zip = self.find("#id_zip")
        zip.clear()
        zip.send_keys("941091")
        self.find("#signup-form-submit").click() 
        sleep(2)
        return self.find("#street_e ul li").text ==\
            "Enter a valid adress, city, state, and/or zip."
    
    def test_23(self):
        """
        password must be at least 6 characters
        """
        # pass1
        pass1 = self.find("#id_password")
        pass1.clear()
        pass1.send_keys("12345")
        self.find("#signup-form-submit").click()
        sleep(2)
        return self.find("#password_e ul li").text.__contains__(\
            "Ensure this value has at least 6 characters ")
            
    def test_24(self):
        """
        password and corfirmation must be the same
        """
        pass1 = self.find("#id_password")
        pass1.clear()
        pass1.send_keys("1234567")
        pass2 = self.find("#id_confirm_password")
        pass2.clear()
        pass2.send_keys("1234467")
        self.find("#signup-form-submit").click() 
        sleep(2)
        return self.find("#password_e ul li").text ==\
            "Passwords don't match."
            
