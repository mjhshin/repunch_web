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
from repunch.settings import PRODUCTION_SERVER

from apps.public.forms import SUBJECT_PREFIX

def test_public_pages():
    test = SeleniumTest()
    
    parts = [
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
    except Exception as e:
        print e 
        parts[1]['test_message'] = str(e)
    else:
        parts[1]['success'] = True
    
    ##########  FAQ page navigable
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
    try:
        test.action_chain(1, selectors, type="xpath") # ACTION!
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
    else:
        parts[2]['success'] = True
    
    ##########  About page navigable
    # ACTION!
    test.find("//nav[@id='header-menu']/a[@href='" +\
           reverse("public_about") + "']", type="xpath").click()
    selectors = [] 
    # about member photos
    for i in range(1, 6):
        selectors.append("//div[@id='the-team']/" +\
            "div[@class='the-team-member tooltip'][" +\
            str(i) + "]")
    # ACTION!
    try:
        test.action_chain(1, selectors, action="move", type="xpath")
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
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
        test.action_chain(3, selectors, type="xpath") # ACTION!
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
    else:
        parts[4]['success'] = True
        
    test.new_driver()
    
    ##########  FAQ email form working
    test.open(reverse("public_faq")) # ACTION!
    selectors = (
        ("#id_full_name", "Test User X"),
        ("#id_email", "test@test.com"),
        ("#id_message", "FAQ page. This is a test - ignore it.")
    )
    try:
        test.action_chain(0, selectors, action="send_keys") # ACTION!
        test.find("//form[@id='make-question-form']/a", 
            type="xpath").click()
        sleep(1)
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
    else:
        parts[5]['success'] =\
            test.is_current_url(reverse("public_thank_you"))
        
    ##########  FAQ email sent
    sleep(4) # wait for the email to register in gmail
    mail = Mail()
    try:
        if PRODUCTION_SERVER:
             parts[6]['success'] = parts[5]['success']
        else:
            parts[6]['success'] =\
                mail.is_mail_sent(SUBJECT_PREFIX + "Test User X")
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
            
    ##########  FAQ email form all fields required
    test.open(reverse("public_faq"))
    sleep(1)
    selectors = (
        ("#id_full_name", "  "),
        ("#id_email", "  "),
        ("#id_message", "  ")
    )
    try:
        test.action_chain(0, selectors, action="send_keys") # ACTION!
        test.find("//form[@id='make-question-form']/a", 
            type="xpath").click()
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
    else:
        parts[7]['success'] = len(test.find(".errorlist",
            multiple=True)) == 3
    sleep(1)
            
    ##########  Contact Us email form working
    test.open(reverse("public_contact")) # ACTION!
    selectors = (
        ("#id_full_name", "Test User Y"),
        ("#id_email", "test@test.com"),
        ("#id_message", "Contact Us page. This is a test - ignore it.")
    )
    try:
        test.action_chain(0, selectors, action="send_keys") # ACTION!
        test.find("//form[@id='contact-form']/a", 
            type="xpath").click()
        sleep(1)
    except Exception as e:
        print e
        parts[8]['test_message'] = str(e)
    else:
        parts[8]['success'] =\
            test.is_current_url(reverse("public_thank_you"))
         
    ##########  Contact Us email sent
    sleep(4) # wait for the email to register in gmail
    try:
        if PRODUCTION_SERVER:
            parts[9]['success'] = parts[8]['success']
        else:
            parts[9]['success'] =\
                mail.is_mail_sent(SUBJECT_PREFIX + "Test User Y")
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
            
    ##########  Contact Us email form all fields required
    test.open(reverse("public_contact")) # ACTION!
    selectors = (
        ("#id_full_name", "   "),
        ("#id_email", "   "),
        ("#id_message", "   ")
    )
    try:
        test.action_chain(0, selectors, action="send_keys") # ACTION!
        test.find("//form[@id='contact-form']/a", 
            type="xpath").click()
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
    else:
        parts[10]['success'] =  len(test.find(".errorlist",
            multiple=True)) == 3
    sleep(2)
    
    # END TEST
    mail.logout()
    test.results.append(section)
    
    # END OF ALL TESTS
    return test.tear_down()
    
    
        
        
        
        
        
        
        
        
        
