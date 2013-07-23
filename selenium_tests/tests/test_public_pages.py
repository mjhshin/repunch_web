"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse
from selenium_tests import get_test_case_class

class PublicPagesTestCase(get_test_case_class()):
    """
    Test that all public pages are accessible.
    """
    
    def test_from_home_page_to_all(self):
        """
        Loads the home page and clicks around to access all public
        pages.
        """
        self.open(reverse("public_home"))
        

