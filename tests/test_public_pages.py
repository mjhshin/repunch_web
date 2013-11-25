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

def test_public_pages():
    print "\ntest_public_pages:"
    print "--------------------"   
     
    test = SeleniumTest("PUBLIC_PAGES", [
        {'test_name': "Home page navigable"},
        {'test_name': "Learn page navigable"},
        {'test_name': "FAQ page navigable"},
        {'test_name': "About page navigable"},
        {'test_name': "Footer elements navigable"},
        {'test_name': "FAQ email form working"},
        {'test_name': "FAQ email sent"},
        {'test_name': "FAQ email form all fields required"},
        {'test_name': "Contact Us email form working"},
        {'test_name': "Contact Us email sent"},
        {'test_name': "Contact Us email form all fields required"},
    ])
    
    ##########  Home page navigable
    def test_0():
        test.open(reverse("public_home"))
        sleep(2)
        return test.is_current_url(reverse("public_home"))
        
    test.testit(test_0)
    
    ##########  Learn page navigable
    def test_1():
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
        test.action_chain(1, selectors)
        return True
        
    test.testit(test_1)
    
    ##########  FAQ page navigable
    def test_2():
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
        test.action_chain(1, selectors, type="xpath")
        return True
        
    test.testit(test_2)
    
    ##########  About page navigable
    def test_3():
        test.find("//nav[@id='header-menu']/a[@href='" +\
               reverse("public_about") + "']", type="xpath").click()
        selectors = [] 
        # about member photos
        for i in range(1, 6):
            selectors.append("//div[@id='the-team']/" +\
                "div[@class='the-team-member tooltip'][" +\
                str(i) + "]")
        test.action_chain(1, selectors, action="move", type="xpath")
        return True
        
    test.testit(test_3)
    
    ##########  Footer elements navigable
    def test_4():
        selectors = []
        for i in range(1, 5): # TOS, PP, Contact, Jobs
            selectors.append("//ul[@id='footer-menu']/li[" +\
                str(i) + "]/a[1]")
        # facebook and twitter
        selectors.append("//ul[@id='footer-menu']/li[5]/a[1]")
        selectors.append("//ul[@id='footer-menu']/li[5]/a[2]")
        test.action_chain(3, selectors, type="xpath") # ACTION!
        return True
        
    test.testit(test_4)
    
    test.new_driver()
    
    ##########  FAQ email form working
    def test_5():
        test.open(reverse("public_faq"))
        selectors = (
            ("#id_full_name", "Test User X"),
            ("#id_email", "test@test.com"),
            ("#id_message", "FAQ page. This is a test - ignore it.")
        )
        test.action_chain(0, selectors, action="send_keys") # ACTION!
        test.find("//form[@id='make-question-form']/a", 
            type="xpath").click()
        sleep(1)
        return test.is_current_url(reverse("public_thank_you"))
        
    test.testit(test_5)
    
    if SeleniumTest.CHECK_SENT_MAIL:
        mail = Mail()
    
    ##########  FAQ email sent
    def test_6():
        if SeleniumTest.CHECK_SENT_MAIL:
            sleep(4) # wait for the email to register in gmail
            return mail.is_mail_sent(SUBJECT_PREFIX + "Test User X")
        else:
            return parts[5]['success']
        
    test.testit(test_6)
    
    ##########  FAQ email form all fields required
    def test_7():
        test.open(reverse("public_faq"))
        sleep(1)
        selectors = (
            ("#id_full_name", "  "),
            ("#id_email", "  "),
            ("#id_message", "  ")
        )
        test.action_chain(0, selectors, action="send_keys") 
        test.find("//form[@id='make-question-form']/a", 
            type="xpath").click()
        return len(test.find(".errorlist",
            multiple=True)) == 3
            
    test.testit(test_7)    
    
    sleep(1)
            
    ##########  Contact Us email form working
    def test_8():
        test.open(reverse("public_contact"))
        selectors = (
            ("#id_full_name", "Test User Y"),
            ("#id_email", "test@test.com"),
            ("#id_message", "Contact Us page. This is a test - ignore it.")
        )
        test.action_chain(0, selectors, action="send_keys") # ACTION!
        test.find("//form[@id='contact-form']/a", 
            type="xpath").click()
        sleep(1)
        return test.is_current_url(reverse("public_thank_you"))
            
    test.testit(test_8)
        
    ##########  Contact Us email sent
    def test_9():
        if SeleniumTest.CHECK_SENT_MAIL:
            sleep(4) # wait for the email to register in gmail
            return mail.is_mail_sent(SUBJECT_PREFIX + "Test User Y")
        else:
            return parts[8]['success']
            
    test.testit(test_9)
            
    ##########  Contact Us email form all fields required
    def test_10():
        test.open(reverse("public_contact"))
        selectors = (
            ("#id_full_name", "   "),
            ("#id_email", "   "),
            ("#id_message", "   ")
        )
        test.action_chain(0, selectors, action="send_keys") 
        test.find("//form[@id='contact-form']/a", 
            type="xpath").click()
        return len(test.find(".errorlist", multiple=True)) == 3
                
    test.testit(test_10)
    sleep(2)
    
    # END TEST
    if SeleniumTest.CHECK_SENT_MAIL: 
        mail.logout()
    
    # END OF ALL TESTS
    return test.tear_down()
    
    
        
        
        
        
        
        
        
        
        
