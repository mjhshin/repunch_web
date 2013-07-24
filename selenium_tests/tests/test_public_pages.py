"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse
from selenium_tests import get_test_case_class

from time import sleep

class PublicPagesTestCase(get_test_case_class()):
    """
    Test that all public pages are accessible.
    """
    
    def test_from_home_page_to_all(self):
        """
        Loads the home page and clicks around to access all public
        pages.
        """
        ### HOME
        # ACTION!
        self.open(reverse("public_home"))
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
        # ACTION!
        # self.action_chain(1, selectors) 
        
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
        # ACTION!
        # self.action_chain(1, selectors, type="xpath")
        
        ### ABOUT
        # ACTION!
        # self.find("//nav[@id='header-menu']/a[@href='" +\
        #        reverse("public_about") + "']", type="xpath").click()
        selectors = [] 
        # about member photos
        for i in range(1, 7):
            selectors.append("//div[@id='the-team']/" +\
                "div[@class='the-team-member tooltip'][" +\
                str(i) + "]")
        # ACTION!
        # self.action_chain(1, selectors, action="move", type="xpath")
        
        # go back to home page via header logo
        # ACTION!
        self.find("//div[@id='header-content']/a[1]",
            type="xpath").click()
        
        ### FOOTER elements
        selectors = []
        for i in range(1, 5): # TOS, PP, Contact, Jobs
            selectors.append("//ul[@id='footer-menu']/li[" +\
                str(i) + "]/a[1]")
        # facebook and twitter
        selectors.append("//ul[@id='footer-menu']/li[5]/a[1]")
        selectors.append("//ul[@id='footer-menu']/li[5]/a[2]")
        # ACTION!
        self.action_chain(1, selectors, type="xpath")
        
        # close all windows
        sleep(2)
        # ACTION!
        self.driver.close()
        sleep(1)
        
        # open the home page again
        # ACTION!
        self.open(reverse("public_home"))
        sleep(1)
        
        
        # TODO SIGNUP
        
        
        
        
        
        # END
        sleep(5)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
