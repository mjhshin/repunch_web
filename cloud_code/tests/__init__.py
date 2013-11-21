"""
Utility methods for cloud_code tests.

These should also be used for SeleniumTests.
"""

class CloudCodeTest(object):
    
    def __init__(self, test_title, tests):
        """
        tests has the following format:
        [ {'test_name': "Test title"}, ... ]
        """
        self._results = []
        section = {
            "section_name": test_title,
            "parts": tests,
        }
        self._results.append(section)
        self.tests = tests
    
    def get_results(self):
        return self._results
    
    def testit(self, test, verbose=True):
        """
        test is a function that must return a bool.
        If a str is returned, then the test is a fail and the str
        is set as the test_message.
        
        test must have a name of test_x where x is the number of the test. 
        """
        test_num = int(test.__name__.split("_")[-1])
        
        if verbose:
            print "Test #%s:" % (str(test_num),)
            
        try:
            result = test()
            if type(result) in (unicode, str):
                self.tests[test_num]["test_message"] = result
            elif type(result) is bool:
                self.tests[test_num]["success"] = result
                
            if verbose:
                print str(type(result) is bool and result)
                
        except Exception as e:
            if verbose:
                print "Error: %s\n\n" % (e, )
                
            self.tests[test_num]["test_message"] = str(e)
