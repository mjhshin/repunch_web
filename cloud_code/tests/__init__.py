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
    
    def testit(self, test_num, test):
        """
        test is a function that must return a bool.
        """
        try:
            self.tests[test_num]["success"] = test()
        except Exception as e:
            print "Error: %s\n%s" %\
                (self.tests[test_num]["test_name"], e)
            self.tests[test_num]["test_message"] = str(e)
