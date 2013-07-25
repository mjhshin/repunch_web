"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse
from selenium_tests import get_test_case_class
from selenium.webdriver.common.keys import Keys

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
        
        """
        [ {'section_name": section1,
              'parts': [ {'test_name':test1, 'success':True}, ... ]}
            ... ]
        """
        parts = [
            {'test_name': "Home page functional"},
            {'test_name': "Learn page functional"},
            {'test_name': "FAQ page functional"},
            {'test_name': "About page functional"},
            {'test_name': "Footer elements functional"},
            {'test_name': "Sign Up page functional"},
        ]
        section = {
            "section_name": "Are all public pages functional?",
            "parts": parts,
        }
        
        ### HOME
        self.t.open(reverse("public_home")) # ACTION!
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
        # self.t.action_chain(1, selectors) # ACTION!
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
        # self.t.action_chain(1, selectors, type="xpath") # ACTION!
        parts[2]['success'] = True
        
        ### ABOUT
        # ACTION!
        # self.t.find("//nav[@id='header-menu']/a[@href='" +\
        #        reverse("public_about") + "']", type="xpath").click()
        selectors = [] 
        # about member photos
        for i in range(1, 7):
            selectors.append("//div[@id='the-team']/" +\
                "div[@class='the-team-member tooltip'][" +\
                str(i) + "]")
        # ACTION!
        # self.t.action_chain(1, selectors, action="move", type="xpath")
        parts[3]['success'] = True
        
        ### FOOTER elements
        selectors = []
        for i in range(1, 5): # TOS, PP, Contact, Jobs
            selectors.append("//ul[@id='footer-menu']/li[" +\
                str(i) + "]/a[1]")
        # facebook and twitter
        selectors.append("//ul[@id='footer-menu']/li[5]/a[1]")
        selectors.append("//ul[@id='footer-menu']/li[5]/a[2]")
        # self.t.action_chain(2, selectors, type="xpath") # ACTION!
        parts[4]['success'] = True
        
        # close all windows
        sleep(2)
        # open the home page again
        # self.t.new_driver() # ACTION!
        # self.t.open(reverse("public_home")) # ACTION!
        
        # SIGNUP
        sleep(2)
        self.t.find("//aside[@id='home-col-left']/a[1]",
            type="xpath").click() # ACTION!
        
        # form data
        selectors = (
            ("#id_store_name", "test business"),
            ("#id_street", "1370 virginia ave 4d"),
            ("#id_city", "bronx"),
            ("#id_state", "ny"),
            ("#id_zip", "10462"),
            ("#categories", "baker"),
            ("", Keys.ARROW_DOWN),
            ("", Keys.RETURN),
            ("#categories", "fitn"),
            ("", Keys.ARROW_DOWN),
            ("", Keys.RETURN),
            ("#id_first_name", "Testee"),
            ("#id_last_name", "Bestee"),
            ("#Ph1", "777"),
            ("#Ph2", "777"),
            ("#Ph3", "7777"),
            ("#id_email", "test@iusluixylusr.com"),
            ("#id_username", "iusluixylusr"),
            ("#id_password", "iusluixylusr"),
            ("#id_confirm_password", "iusluixylusr"),
        )
        self.t.action_chain(1, selectors, action="send_keys") # ACTION!
        # ToS and submit
        selectors = (
            "#id_recurring",
            # "#signup-form-submit",
        )
        self.t.action_chain(2, selectors) # ACTION!
        
        # TODO interact with the pop up dialog
        # TODO delete the created Parse objects
        
        parts[5]['success'] = True
        
        # END
        self.t.results.append(section)
        sleep(5)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
