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
    
    ##########  Footer elements navigable
    def test_4():
        selectors = []
        for i in range(1, 5): # TOS, PP, Contact, Jobs
            selectors.append("//ul[@id='footer-menu']/li[" +\
                str(i) + "]/a[1]")
        # facebook and twitter
        selectors.append("//ul[@id='footer-menu']/li[5]/a[1]")
        selectors.append("//ul[@id='footer-menu']/li[5]/a[2]")
        test.action_chain(3, selectors, type="xpath") 
        return True
    
    ##########  FAQ email form working
    def test_5():
        test.new_driver()
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
        
    ##########  FAQ email sent
    def test_6():
        if SeleniumTest.CHECK_SENT_MAIL:
            globals()["mail"] = Mail()
            sleep(4) # wait for the email to register in gmail
            return globals()["mail"].is_mail_sent(\
                SUBJECT_PREFIX + "Test User X")
        else:
            return (True, "Test skipped.")
        
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
        sleep(1)
        return len(test.find(".errorlist",
            multiple=True)) == 3
            
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
            
    ##########  Contact Us email sent
    def test_9():
        if SeleniumTest.CHECK_SENT_MAIL:
            sleep(4) # wait for the email to register in gmail
            return globals()["mail"].is_mail_sent(\
                SUBJECT_PREFIX + "Test User Y")
        else:
            return (True, "Test skipped.")
            
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
        sleep(1)
        return len(test.find(".errorlist", multiple=True)) == 3
        
    for i in range(11):
        test.testit(locals()["test_%s" % (str(i),)])
    
    # END TEST
    if SeleniumTest.CHECK_SENT_MAIL: 
        globals()["mail"].logout()
    
    # END OF ALL TESTS
    return test.tear_down()
    
    
        
        
        
        
        
        
        
        
        
