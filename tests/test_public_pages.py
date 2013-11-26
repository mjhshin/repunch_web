"""
Selenium test for public pages.

I know that this is not how tests are done in Django. 
The justification for this is that we are not using Django Models but
Parse Objects and services so yea.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from libs.imap import Mail
from tests import SeleniumTest

from apps.public.forms import SUBJECT_PREFIX

class TestPublicPages(SeleniumTest):

    def __init__(self):
        super(TestPublicPages, self).__init__(False)

    def test_0(self):
        """
        Home page navigable
        """
        self.open(reverse("public_home"))
        sleep(2)
        return self.is_current_url(reverse("public_home"))
        
    def test_1(self):
        """
        Learn page navigable
        """
        selectors = (
            # learn page link
            "#header-menu a[href='" + reverse("public_learn") + "']",
            # tabs
            "#tabMessages",
            "#tabFeedback",
            "#tabAnalytics",
            "#tabSocial",
            "#tabPlans-pricing", 
        )
        self.action_chain(1, selectors)
        return True
        
    def test_2(self):
        """
        FAQ page navigable
        """
        selectors = [
            # faq page
            "//nav[@id='header-menu']/a[@href='" +\
                reverse("public_faq") + "']", 
        ]
        # faq accordion buttons
        for i in range(1, 14):
            selectors.append("//div[@id='faq-content']/aside[@" +\
                "class='col1']/"+\
                "div[" + str(i) + "]/div[@class='accordionButton']")
        self.action_chain(1, selectors, type="xpath")
        return True
        
    def test_3(self):
        """
        About page navigable
        """
        self.find("//nav[@id='header-menu']/a[@href='" +\
               reverse("public_about") + "']", type="xpath").click()
        selectors = [] 
        # about member photos
        for i in range(1, 6):
            selectors.append("//div[@id='the-team']/" +\
                "div[@class='the-team-member tooltip'][" +\
                str(i) + "]")
        self.action_chain(1, selectors, action="move", type="xpath")
        return True
    
    def test_4(self):
        """
        Footer elements navigable
        """
        selectors = []
        for i in range(1, 5): # TOS, PP, Contact, Jobs
            selectors.append("//ul[@id='footer-menu']/li[" +\
                str(i) + "]/a[1]")
        # facebook and twitter
        selectors.append("//ul[@id='footer-menu']/li[5]/a[1]")
        selectors.append("//ul[@id='footer-menu']/li[5]/a[2]")
        self.action_chain(3, selectors, type="xpath") 
        return True
    
    def test_5(self):
        """
        FAQ email form working
        """
        self.new_driver()
        self.open(reverse("public_faq"))
        sleep(2)
        selectors = (
            ("#id_full_name", "Test User X"),
            ("#id_email", "test@self.com"),
            ("#id_message", "FAQ page. This is a test - ignore it.")
        )
        self.action_chain(0, selectors, action="send_keys") # ACTION!
        self.find("//form[@id='make-question-form']/a", 
            type="xpath").click()
        sleep(1)
        return self.is_current_url(reverse("public_thank_you"))
        
    def test_6(self):
        """
        FAQ email sent
        """
        if self.CHECK_SENT_MAIL:
            self.mail = Mail()
            sleep(4) # wait for the email to register in gmail
            return self.mail.is_mail_sent(\
                SUBJECT_PREFIX + "Test User X")
        else:
            return (True, "Test skipped.")
        
    def test_7(self):
        """
        FAQ email form all fields required
        """
        self.open(reverse("public_faq"))
        sleep(1)
        selectors = (
            ("#id_full_name", "  "),
            ("#id_email", "  "),
            ("#id_message", "  ")
        )
        self.action_chain(0, selectors, action="send_keys") 
        self.find("//form[@id='make-question-form']/a", 
            type="xpath").click() 
        sleep(1)
        return len(self.find(".errorlist",
            multiple=True)) == 3
            
    def test_8(self):
        """
        Contact Us email form working
        """
        self.open(reverse("public_contact"))
        selectors = (
            ("#id_full_name", "Test User Y"),
            ("#id_email", "test@self.com"),
            ("#id_message", "Contact Us page. This is a test - ignore it.")
        )
        self.action_chain(0, selectors, action="send_keys") # ACTION!
        self.find("//form[@id='contact-form']/a", 
            type="xpath").click()
        sleep(1)
        return self.is_current_url(reverse("public_thank_you"))
            
    def test_9(self):
        """
        Contact Us email sent
        """
        if self.CHECK_SENT_MAIL:
            sleep(4) # wait for the email to register in gmail
            return self.mail.is_mail_sent(\
                SUBJECT_PREFIX + "Test User Y")
        else:
            return (True, "Test skipped.")
            
    def test_10(self):
        """
        Contact Us email form all fields required
        """
        if self.CHECK_SENT_MAIL: 
            self.mail.logout()
            
        self.open(reverse("public_contact"))
        selectors = (
            ("#id_full_name", "   "),
            ("#id_email", "   "),
            ("#id_message", "   ")
        )
        self.action_chain(0, selectors, action="send_keys") 
        self.find("//form[@id='contact-form']/a", 
            type="xpath").click()
        sleep(1)
        return len(self.find(".errorlist", multiple=True)) == 3
        
