"""
Tests that all Punch Codes in PunchCode.json are unique and exists.
All errors are logged in errors.txt (if errors exist)

This must be run on this directory.
"""

import re

def get_punch_code_count(punch_code, punch_codes):
    return len(re.findall(r'"punch_code": "%s"' %\
        (punch_code,), punch_codes))

def run_test():

    with open("PunchCode.json", "r") as data:
        punch_codes = data.read()
        
    with open("errors.txt", "a+") as errors:
        for i in range(0, 100000):
            punch_code = str(i).zfill(5)
            punch_code_count =\
                get_punch_code_count(punch_code, punch_codes)
            
            print "Punch Code: %s exist and unique? \t%s" %\
                (punch_code, str(punch_code_count == 1))
                
            if punch_code_count == 0:
                errors.write("Punch Code: %s DNE" % punch_code)
            elif punch_code_count > 1:
                errors.write("Punch Code: %s has %s duplicates" %\
                    (punch_code, str(punch_code_count - 1)))


if __name__ == "__main__":
    run_test()
