"""
Selenium test for public pages.

I know that this is not how tests are done in Django. 
The justification for this is that we are not using Django Models but
Parse Objects and services so yea.
"""

from django.core.urlresolvers import reverse
from selenium.webdriver.common.keys import Keys
from time import sleep

from tests import SeleniumTest

def test_public_pages():
    """        
    # TODO FAQ Form
    # TODO Contact Us Form
    """
    test = SeleniumTest()
    
    parts = [
        {'test_name': "Home page navigable"},
        {'test_name': "Learn page functional"},
        {'test_name': "FAQ page functional"},
        {'test_name': "About page functional"},
        {'test_name': "Footer elements functional"},
    ]
    section = {
        "section_name": "Are all public pages functional?",
        "parts": parts,
    }
    
    ### HOME
    test.open(reverse("public_home")) # ACTION!
    parts[0]['success'] = True
    sleep(1)
    
    ### LEARN
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
    
    ### FAQ
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
    
    ### ABOUT
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
    
    ### FOOTER elements
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
    
    # END TEST
    sleep(2)
    test.results.append(section)
    
    # END OF ALL TESTS
    return test.tear_down()
    
    
        
        
        
        
        
        
        
        
        
