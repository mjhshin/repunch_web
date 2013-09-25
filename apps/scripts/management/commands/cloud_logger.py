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
  
  - In each "log_job" the output of "parse log -n n" is evaluated. 
    We start at n so we only evaluate a small portion of the logs.

  - If the last_log_tag is not in this subset, then we multiply n. 
    We do this until we have a subset of the logs from last_log_tag 
    to the TIP so that we do not miss 1 line of logging.
  
  - If the last_log_tag is the tip, then we do nothing.
    
  - Once we have the subset of the logs we want, we then scan it for
    items in ERRORS. An email is sent containing the log from
    last_log_tag to the tip and last_log_tag is set to the first
    tag encountered starting from the tip.
    
  * e.g.
    parse log -n 10
    -----------------------------------------
    I2013-09-25T19:50:26.947Z] Employee fetched.
    I2013-09-25T19:50:27.149Z] Employee save was successful. 
    I2013-09-25T19:50:27.149Z] Posting to server <---- (last_log_tag)
    I2013-09-25T19:50:47.285Z] v43: Ran cloud function punch for user uNUk7Jsiv9 with:
      Input: {"store_id":....}
      Result: error
    I2013-09-25T19:50:47.537Z] updating existing PatronStore
    I2013-09-25T19:50:47.844Z] PatronStore save was successful.
    I2013-09-25T19:50:47.844Z] Patron... <---- (tip)
    
    The following lob job will then send to EMAILS containing the below
    -------------------------------------------------------------
    I2013-09-25T19:50:27.149Z] Posting to server <---- (last_log_tag)
    I2013-09-25T19:50:47.285Z] v43: Ran cloud function punch for user uNUk7Jsiv9 with:
      Input: {"store_id":....}
      Result: error
    I2013-09-25T19:50:47.537Z] updating existing PatronStore
    I2013-09-25T19:50:47.844Z] PatronStore save was successful.
    I2013-09-25T19:50:47.844Z] Patron... <---- (tip)
    
  - Note from the above that this I2013-09-25T19:50:47.537Z] is a tag.
 
   
"""

import os, subprocess, shlex, re
from time import sleep

from django.core.management.base import BaseCommand
from django.utils import timezone

ERRORS = ["error"]
EMAILS = ["vandolf@repunch.com", "mike@repunch.com"]

PARSE_CODE_DIR = "./cloud_code/development"
PARSE_LOG_CMD = "parse log -n "

LOGJOB_INTERVAL = 10# in seconds

TAG_RE = re.compile(r"(I|E)\d{4,4}-\d{2,2}-\d{2,2}T\d{2,2}:\d{2,2}:\d{2,2}\.\d{3,3}Z]")

class LogJob(object):
    
    def __init__(self, *args, **kwargs):
        # let's start the very first job with a relatively large n
        self.last_log_tag = None
        self.last_log_time = None
        self.n = 500
        
    def log_job(self):
        sp = subprocess.Popen(shlex.split(PARSE_LOG_CMD + str(n)),
            stdout=subprocess.PIPE)
        subset = sp.stdout.read()
        
        # evaluate if first run
        if not self.last_log_tag or not self.last_log_time:
            for error in ERRORS:
                if error in subset:
                    # TODO send_mail(subset)
                    print subset
                    
            # set the last tag and time
            self.last_log_tag = TAG_RE.findall(subset)[-1]
            self.last_log_time = timezone.now()
            return
            
        
        
        
    def work(self):
        self.log_job()
        # sleep if we finished early
        work_time = (self.last_log_time - timezone.now()).seconds
        time_to_sleep = LOGJOB_INTERVAL - work_time
        if time_to_sleep > 0:
            sleep(time_to_sleep)
        self.work()


class Command(BaseCommand):
    def handle(self, *args, **options):
        # first cd to the cloud project
        os.chdir(PARSE_CODE_DIR)
        # now just just ignite the LogJob
        LogJob().work()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        