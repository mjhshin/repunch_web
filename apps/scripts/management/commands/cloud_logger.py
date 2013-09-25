"""
This will run parse log -f indefinitely looking for keywords listed
in ERRORS.

If an item is detected, then a chunk of lines of output is emailed to
EMAILS.
---------------------------------------------------------------------

Implementation:
---------------------------------------------
Since the stdout of subprocess.Popen is blocked until the
subprocess is finished - using parse log -f will not work.
Note that killing the process will result in an empty stdout.

  - Jobs will run every LOGJOB_INTERVAL. 
  
  - In each "log_job" the output of "parse log -n x" is evaluated. 
    We start at x so we only evaluate a small portion of the logs.

  - If the LAST_LOG_TIME is not in this subset, then we multiply x. 
    We do this until we have a subset of the logs from LAST_LOG_TIME 
    to the TIP so that we do not miss 1 line of logging.
  
  - If the LAST_LOG_TIME is the tip, then we do nothing.
    
  - Once we have the subset of the logs we want, we then scan it for
    items in ERRORS. An email is sent containing the log from
    LAST_LOG_TIME to the tip and LAST_LOG_TIME is set to the first
    time tag encountered starting from the tip.
    
  * e.g.
    parse log -n 10
    -----------------------------------------
    I2013-09-25T19:50:26.947Z] Employee fetched.
    I2013-09-25T19:50:27.149Z] Employee save was successful. 
    I2013-09-25T19:50:27.149Z] Posting to server <---- (LAST_LOG_TIME)
    I2013-09-25T19:50:47.285Z] v43: Ran cloud function punch for user uNUk7Jsiv9 with:
      Input: {"store_id":....}
      Result: error
    I2013-09-25T19:50:47.537Z] updating existing PatronStore
    I2013-09-25T19:50:47.844Z] PatronStore save was successful.
    I2013-09-25T19:50:47.844Z] Patron... <---- (tip)
    
    The following lob job will then send to EMAILS containing the below
    -------------------------------------------------------------
    I2013-09-25T19:50:27.149Z] Posting to server <---- (LAST_LOG_TIME)
    I2013-09-25T19:50:47.285Z] v43: Ran cloud function punch for user uNUk7Jsiv9 with:
      Input: {"store_id":....}
      Result: error
    I2013-09-25T19:50:47.537Z] updating existing PatronStore
    I2013-09-25T19:50:47.844Z] PatronStore save was successful.
    I2013-09-25T19:50:47.844Z] Patron... <---- (tip)
 
   
"""

import os, subprocess, shlex, re
from time import sleep

from django.core.management.base import BaseCommand

ERRORS = ["error"]
EMAILS = ["vandolf@repunch.com", "mike@repunch.com"]

PARSE_CODE_DIR = "./cloud_code/production"
PARSE_LOG_CMD = "parse log -n"

LOGJOB_INTERVAL = 3# in seconds

def log_job():
    sp = subprocess.Popen(shlex.split(PARSE_LOG_CMD),stdout=subprocess.PIPE, cwd=PARSE_CODE_DIR)
    # now evaluate the stdout and look for ERRORS
    print sp.stdout.read()

class Command(BaseCommand):
    def handle(self, *args, **options):
        log_job()
