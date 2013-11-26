"""
Utility methods for cloud_code tests.

These should also be used for SeleniumTests.
"""

import re

from parse.apps.accounts.models import Account

UN_CAMEL_RE = re.compile(r"([a-z0-9])([A-Z])")

class CloudCodeTest(object):

    # This User exists solely for testing CloudCode.
    # It must have a Store, Employee, and Patron pointers.
    USER = {
        "email": "cloudcode@repunch.com",
        "password": "123456",
    }
    
    def __init__(self, fetch_user=True, verbose=False):
        """
        tests has the following format:
        [ {'test_name': "Test title"}, ... ]
        """
        self.verbose = verbose
        
        name = UN_CAMEL_RE.sub(r'\1 \2', self.__class__.__name__)
        
        if self.verbose:
            print "\n" + name 
            print "--------------------------------------------------"
        
        self._tests = []
        self._results = {
            "section_name": name,
            "parts": self._tests,
        }
        
        if fetch_user:
            self.account = Account.objects().get(email=\
                self.USER['email'], include="Patron,Store,Employee")
            self.patron = self.account.patron
            self.store = self.account.store
            self.employee = self.account.employee
    
    def get_results(self):
        """
        Evaluates all tests defined within self.
        {
            test_0: <function test_0 >, ...
        }
        """
        test_nums = [ int(k.split("_")[-1]) for
            k in dir(self) if k.startswith("test_")]
        # need to sort
        test_nums.sort()

        for t in test_nums:
            self.testit(getattr(self, "test_%d" % (t,)), t)
            
        return self._results
    
    def testit(self, test_func, test_num=None):
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
        
        if self.verbose:
            log = "Test #%s:\t" % (str(test_num),)
            
        test = {"test_name": test_func.__doc__}       
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
                
            if self.verbose:
                if type(result) is bool and result:
                    log += "Success"
                else:
                    log += "Fail - %s" % (result,)
                
        except Exception as e:
            if self.verbose:
                log += "Error: %s" % (e, )
                
            test["test_message"] = str(e)
        finally:
            if self.verbose:
                print log
