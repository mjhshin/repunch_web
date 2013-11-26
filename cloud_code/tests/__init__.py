"""
Utility methods for cloud_code tests.

These should also be used for SeleniumTests.
"""

import re

from parse.apps.accounts.models import Account

UN_CAMEL_RE = re.compile(r"([a-z0-9])([A-Z])")

class CloudCodeTest(object):

    # This User exists solely for testing.
    # It must have a Store, Employee, and Patron pointers.
    USER = {
        "username": "repunchtest@repunch.com",
        "email": "repunchtest@repunch.com",
        "password": "123456",
    }
    
    def __init__(self, fetch_user=True):
        """
        tests has the following format:
        [ {'test_name': "Test title"}, ... ]
        """
        self.name = UN_CAMEL_RE.sub(r'\1 \2', self.__class__.__name__)
        
        self._tests = []
        self._results = {
            "section_name": self.name,
            "parts": self._tests,
        }
        
        if fetch_user:
            self.account = Account.objects().get(email=\
                self.USER['email'], include="Patron,Store,Employee")
            self.patron = self.account.patron
            self.store = self.account.store
            self.employee = self.account.employee
            
    def print_tests(self):
        """
        Prints all the tests' test_names in order.
        """
        for name in self._get_sorted_tests():
            print "Test #%s:\t%s" %\
                (name.split("_")[-1], getattr(self, name).__doc__.strip())
    
    def get_results(self, verbose=False):
        """
        Evaluates all tests defined within self.
        {
            test_0: <function test_0 >, ...
        }
        """
        if verbose:
            print "\n" + self.name 
            print "--------------------------------------------------"
            
        for name in self._get_sorted_tests():
            self._testit(getattr(self, name),
                int(name.split("_")[-1]), verbose=verbose)
            
        return self._results
        
    def _get_sorted_tests(self):
        names = [ k for k in dir(self) if k.startswith("test_") ]
        names.sort(key=lambda n: int(n.split("_")[-1]))
        return names
    
    def _testit(self, test_func, test_num=None, verbose=False):
        """
        test is a function that must return a bool.
        If a str is returned, then the test is a fail and the str
        is set as the test_message.
        
        test must have a name of test_x where x is the number of the test. 
        It should also have a doc string to be used as the test name 
        or description.
        """
        if test_num is None:
            test_num = int(test.__name__.split("_")[-1])
        
        if verbose:
            log = "Test #%s:\t" % (str(test_num),)
            
        test = {"test_name": test_func.__doc__.strip()}       
        self._tests.append(test)
            
        try:
            result = test_func()
            result_type = type(result)
            
            if result_type in (unicode, str):
                test["test_message"] = result
                
            elif result_type is bool:
                test["success"] = result
                
            elif result_type in (tuple, list):
                test["success"] = result[0]
                test["test_message"] = result[1]
                
            if verbose:
                if type(result) is bool and result:
                    log += "Success"
                else:
                    log += "Fail - %s" % (result,)
                
        except Exception as e:
            if verbose:
                log += "Error: %s" % (e, )
                
            test["test_message"] = str(e)
        finally:
            if verbose:
                print log
