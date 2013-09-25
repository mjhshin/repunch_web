"""
This will run parse log -f indefinitely looking for keywords listed
in ERRORS.

If an item is detected, then a chunk of lines of output is emailed to
EMAILS.
"""

ERRORS = ["error"]
EMAILS = ["vandolf@repunch.com", "mike@repunch.com"]

import subprocess, os

os.chdir("./cloud_code/development")

s = subprocess.Popen("parse log -n 10".split(), stdout=subprocess.PIPE)
log = ""
while True:
    line = s.stdout.readline()
    if not line:
        break
    else:
        log += line
        
        
print log
