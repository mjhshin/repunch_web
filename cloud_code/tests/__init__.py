"""
Utility methods for cloud_code tests.

These should also be used for SeleniumTests.
"""


class CloudCodeTest(object):

    VERBOSE = True
    
    def __init__(self, tests):
        """
        tests has the following format:
        [ {'test_name': "Test title"}, ... ]
        """
        self._results = [{
            "section_name": self.__class__.__name__,
            "parts": tests,
        }]
        self._tests = tests
    
    def get_results(self):
        """
        Evaluates all tests defined within self.
        {
            test_0: <function test_0 > | <function <lambda> >, ...
        }
        """
        test_nums = [ int(k.split("_")[-1]) for
            k in dir(self) if k.startswith("test_")]
        # need to sort
        test_nums.sort()

        for t in test_nums:
            self.testit(getattr(self, "test_%d" % (t,)), t)
            
        return self._results
    
    def testit(self, test, test_num=None):
        """
        test is a function that must return a bool.
        If a str is returned, then the test is a fail and the str
        is set as the test_message.
        
        test must have a name of test_x where x is the number of the test. 
        test may be a lambda function, in whcih case test_num must
        be provided.
        """
        verbose = self.VERBOSE
                
        if test_num is None:
            test_num = int(test.__name__.split("_")[-1])
        
        if verbose:
            log = "Test #%s:\t" % (str(test_num),)
            
        try:
            result = test()
            result_type = type(result)
            
            if result_type in (unicode, str):
                self._tests[test_num]["test_message"] = result
            elif result_type is bool:
                self._tests[test_num]["success"] = result
            elif result_type in (tuple, list):
                self._tests[test_num]["success"] = result[0]
                self._tests[test_num]["test_message"] = result[1]
                
            if verbose:
                if type(result) is bool and result:
                    log += "Success"
                else:
                    log += "Fail - %s" % (result,)
                
        except Exception as e:
            if verbose:
                log += "Error: %s\n\n" % (e, )
                
            self._tests[test_num]["test_message"] = str(e)
        finally:
            if verbose:
                print log
