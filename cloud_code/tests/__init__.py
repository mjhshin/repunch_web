"""
Utility methods for cloud_code tests.

These should also be used for SeleniumTests.
"""


class CloudCodeTest(object):

    VERBOSE = True
    
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
    
    def testit(self, test):
        """
        test is a function that must return a bool.
        If a str is returned, then the test is a fail and the str
        is set as the test_message.
        
        test must have a name of test_x where x is the number of the test. 
        """
        verbose = self.VERBOSE
                
        test_num = int(test.__name__.split("_")[-1])
        
        if verbose:
            log = "Test #%s:\t" % (str(test_num),)
            
        try:
            result = test()
            result_type = type(result)
            
            if result_type in (unicode, str):
                self.tests[test_num]["test_message"] = result
            elif result_type is bool:
                self.tests[test_num]["success"] = result
            elif result_type in (tuple, list):
                self.tests[test_num]["success"] = result[0]
                self.tests[test_num]["test_message"] = result[1]
                
            if verbose:
                if type(result) is bool and result:
                    log += "Success"
                else:
                    log += "Fail - %s" % (result,)
                
        except Exception as e:
            if verbose:
                log += "Error: %s\n\n" % (e, )
                
            self.tests[test_num]["test_message"] = str(e)
        finally:
            if verbose:
                print log
