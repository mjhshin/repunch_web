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
        self.action_chain(1, selectors)
        
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
        self.action_chain(1, selectors, type="xpath")
        
        ### ABOUT
        self.find("//nav[@id='header-menu']/a[@href='" +\
                reverse("public_about") + "']", type="xpath").click()
        selectors = [] 
        # about member photos
        for i in range(1, 7):
            selectors.append("//div[@id='the-team']/" +\
                "div[@class='the-team-member tooltip'][" +\
                str(i) + "]")
        self.action_chain(1, selectors, action="move", type="xpath")
        
        # END
        sleep(5)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
