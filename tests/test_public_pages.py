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
from repunch.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from tests import SeleniumTest

SENT_MAILBOX = "[Gmail]/Sent Mail"

def test_public_pages():
    test = SeleniumTest()
    mail = Mail(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    
    parts = [
        {'test_name': "Home page navigable"},
        {'test_name': "Learn page navigable"},
        {'test_name': "FAQ page navigable"},
        {'test_name': "About page navigable"},
        {'test_name': "Footer elements navigable"},
        {'test_name': "FAQ email form working"},
        {'test_name': "FAQ email sent"},
        {'test_name': "Contact Us email form working"},
        {'test_name': "Contact Us email sent"},
    ]
    section = {
        "section_name": "Are all public pages functional?",
        "parts": parts,
    }
    
    ##########  Home page navigable
    test.open(reverse("public_home")) # ACTION!
    parts[0]['success'] = True
    sleep(1)
    
    ##########  Learn page navigable
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
    try:
        test.action_chain(1, selectors) # ACTION!
    except Exception:
        pass # don't really need to set success to False
    else:
        parts[1]['success'] = True
    
    ##########  FAQ page navigable
    selectors = [
        # faq page
        "//nav[@id='header-menu']/a[@href='" +\
            reverse("public_faq") + "']", 
    ]
    # faq accordion buttons
    for i in range(1, 15):
        selectors.append("//div[@id='faq-content']/aside/"+\
            "div[" + str(i) + "]/div[@class='accordionButton']")
    try:
        test.action_chain(1, selectors, type="xpath") # ACTION!
    except Exception:
        pass
    else:
        parts[2]['success'] = True
    
    ##########  About page navigable
    # ACTION!
    test.find("//nav[@id='header-menu']/a[@href='" +\
           reverse("public_about") + "']", type="xpath").click()
    selectors = [] 
    # about member photos
    for i in range(1, 7):
        selectors.append("//div[@id='the-team']/" +\
            "div[@class='the-team-member tooltip'][" +\
            str(i) + "]")
    # ACTION!
    try:
        test.action_chain(1, selectors, action="move", type="xpath")
    except Exception:
        pass
    else:
        parts[3]['success'] = True
    
    ##########  Footer elements navigable
    selectors = []
    for i in range(1, 5): # TOS, PP, Contact, Jobs
        selectors.append("//ul[@id='footer-menu']/li[" +\
            str(i) + "]/a[1]")
    # facebook and twitter
    selectors.append("//ul[@id='footer-menu']/li[5]/a[1]")
    selectors.append("//ul[@id='footer-menu']/li[5]/a[2]")
    try:
        test.action_chain(2, selectors, type="xpath") # ACTION!
    except Exception:
        pass
    else:
        parts[4]['success'] = True
        
    test.new_driver()
        
    ##########  FAQ email form working
    test.open(reverse("public_faq")) # ACTION!
    selectors = (
        ("#id_full_name", "Test User"),
        ("#id_email", "test@test.com"),
        ("#id_message", "This is a test. Ignore this.")
    )
    try:
        test.action_chain(1, selectors, action="send_keys") # ACTION!
        test.find("//form[@id='make-question-form']/a", 
            type="xpath").click()
    except Exception:
        pass
    else:
        parts[5]['success'] = True
    sleep(3) # wait for the email to register in gmail
    mail.select_mailbox(SENT_MAILBOX)
    
    
    ##########  Contact Us email form working
    test.open(reverse("public_contact")) # ACTION!
    
    # END TEST
    sleep(2)
    test.results.append(section)
    
    # END OF ALL TESTS
    return test.tear_down()
    
    
        
        
        
        
        
        
        
        
        
