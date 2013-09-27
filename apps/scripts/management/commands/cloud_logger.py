"""
#######################################
IMPORTANT! 
------------------------
1) Must have the parse tool installed!
   - curl -s https://www.parse.com/downloads/cloud_code/installer.sh | sudo /bin/bash
2) Non-ascii characters will crash parse log tool! (Currently).
3) Unfortunately, I can't get this to run using cron via django management commands.
   So, just run "python manage.py cloud_logger start &; disown" in order to close
   the terminal it is running on without killing it.
4) Do not just kill this process! Use python manage.py cloud_logger stop.
----------------------------------------------------------------------

#########################
NOTE
----------------------
1) apps.scripts.models.LogBoss' sole purpose is to ensure that only 1 LogJob process
   is running at once.
----------------------------

########################
Description
-----------------------------------
This will run parse log -f indefinitely looking for keywords listed
in ERRORS.

If an item is detected, then a chunk of lines of output is emailed to
EMAILS.
---------------------------------------------------------------------

################################
Implementation:
---------------------------------------------
Since the stdout of subprocess.Popen is blocked until the
subprocess is finished - using parse log -f will not work.
Note that killing the process will result in an empty stdout.

  - Jobs will run every LOGJOB_INTERVAL. 
  
  - In each "log_job" the output of "parse log -n n" is evaluated. 
    We start at n so we only evaluate a small portion of the logs.

  - If the last_log_tag is not in this subset, then we add to n. 
    We do this until we have a subset of the logs from last_log_tag 
    to the TIP so that we do not miss 1 line of logging.
  
  - If the last_log_tag is the tip, then we do nothing but set 
    the last_log_tag encountered starting from the tip.
    
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
    
    The following log job will then send to EMAILS containing the below
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

import os, sys, subprocess, shlex, re
from time import sleep
from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from apps.scripts.models import LogBoss
from repunch.settings import DEBUG, EMAIL_FROM, FS_SITE_DIR

ERRORS = ["error"]
EMAILS = ["vandolf@repunch.com", "mike@repunch.com"]

if DEBUG:
    PARSE_CODE_DIR = "./cloud_code/production"
else:
    PARSE_CODE_DIR = FS_SITE_DIR + "/cloud_code/production"
    
PARSE_LOG_CMD = "parse log -n "

LOGJOB_INTERVAL = 40 # in seconds

TAG_RE = re.compile(r"[IE]\d{4,4}\-\d{2,2}\-\d{2,2}T\d{2,2}\:\d{2,2}\:\d{2,2}\.\d{3,3}Z]", re.DOTALL)

class LogJob(object):

    START_N = 50
    N_ADDER = 200 # may want to make this bigger
    
    def __init__(self, *args, **kwargs):
        # let's start the very first job with a relatively large n
        self.last_log_tag = None
        self.last_log_time = None
        self.n = LogJob.START_N
        self.first_run = True
        
        # send an email
        specs = "cloud_logger running with ERRORS = " + str(ERRORS) +\
            "\nEMAILS = " + str(EMAILS) +\
            "\nLOGJOB_INTERVAL = " + str(LOGJOB_INTERVAL)
        
        send_mail("Repunch Cloud Logger Starting", specs,
                EMAIL_FROM, EMAILS, fail_silently=not DEBUG)
        
    def on_stop(self):
        send_mail("Repunch Cloud Logger Manually Stopped",
            "cloud_logger has been manually terminated",
            EMAIL_FROM, EMAILS, fail_silently=not DEBUG)
        
        
    def send(self, log):
        if not self.first_run:
            send_mail("Repunch Cloud Code Error", log, EMAIL_FROM, 
                        EMAILS, fail_silently=not DEBUG)
        else:
            self.first_run = False
        
    def log_job(self):
        sp = subprocess.Popen(shlex.split(PARSE_LOG_CMD +\
            str(self.n)), stdout=subprocess.PIPE)
        subset = str(sp.stdout.read())
        
        # evaluate if first run
        if not self.last_log_tag or not self.last_log_time:
            for error in ERRORS:
                if re.search(error, subset):
                    self.send(subset)
                    break
                    
            # set the last tag and time
            self.last_log_tag = TAG_RE.findall(subset)[-1]
            self.last_log_time = datetime.now()
            return
            
        # check if the last_log_tag is in the subset
        if re.search(self.last_log_tag, subset):
            
            # now get the real subset starting form the last_log_tag
            subset = re.search(r"%s.*" %\
                (self.last_log_tag,), subset, re.DOTALL).group()
            
            # if the subset is nothing but the last_log_tag
            # note that sometimes the last_log_tag is repeated
            if subset.count("\n") -\
                subset.count(self.last_log_tag) in  (0, 1):
                self.last_log_time = datetime.now()
                return
            
            # if it is not then we evaluate it
            for error in ERRORS:
                if re.search(error, subset):
                    self.send(subset)
                    break
            
            # set the last tag and time
            self.last_log_tag = TAG_RE.findall(subset)[-1]
            self.last_log_time = datetime.now()
            return
                    
        # if it is not then lets increase n and try again
        else:
            self.n += LogJob.N_ADDER
            self.log_job()
        
    def work(self):
        try:
            self.log_job()
            # make sure that work_time is at least 1 second or else
            # the difference will be 86399
            sleep(1)
            
            work_time = (datetime.now() - self.last_log_time).seconds
            time_to_sleep = LOGJOB_INTERVAL - work_time
            # sleep more if we finished early
            if time_to_sleep > 0:
                sleep(time_to_sleep)
                
            # start with a small n
            self.n = LogJob.START_N
            
            # check if we are still suppose to be running
            LogBoss.objects.update()
            if LogBoss.objects.all()[0].is_running:
                self.work()
            else:
                self.on_stop()
                
        except Exception as e:
            print "cloud_logger stopped"
            send_mail("Repunch Cloud Logger Stopped", str(e),
                EMAIL_FROM, EMAILS, fail_silently=not DEBUG)

class Command(BaseCommand):
    def handle(self, *args, **options):
    
        count = LogBoss.objects.count()
            
        if "start" in args:
            # run if not already running
            if count == 0:
                boss = LogBoss.objects.create(is_running=False)
            elif count == 1:
                boss = LogBoss.objects.all()[0]
                
            if boss.is_running:
                print "cloud_logger is already running"
                return
                
            # first cd to the cloud project
            os.chdir(PARSE_CODE_DIR)
                
            print "Running cloud_logger"
            boss.is_running = True
            boss.save()
            
            # now just just ignite the LogJob
            LogJob().work()
        
        elif "stop" in args:
            if count == 0:
                print "cloud_logger was not running"
            elif count == 1:
                boss = LogBoss.objects.all()[0]
                
                if boss.is_running:
                    print "stopping cloud_logger"
                    boss.is_running = False
                    boss.save()
                else:
                    print "cloud_logger was not running"
    
        else:
            print "Args must be start or stop"
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
