#!/usr/bin/env python

"""
Wrapper around the parse command line tool for synchronization
between production and development cloud codes.

All edits to the production and development cloud codes are ignored!
Edit the master cloud code instead.
"""

import os, subprocess, shlex, argparse

DEVELOPMENT_COMET_RECEIVE_URL = "http://dev.repunch.com/manage/comet/receive/"
DEVELOPMENT_COMET_RECEIVE_KEY = "384ncocoacxpvgrwecwy"
DEVELOPMENT_GCM_RECEIVE_URL = "http://dev.repunch.com/gcm/receive/"
DEVELOPMENT_GCM_RECEIVE_KEY = "p9wn84m8450yot4ureh"

PRODUCTION_COMET_RECEIVE_URL = "https://www.repunch.com/manage/comet/receive/"
PRODUCTION_COMET_RECEIVE_KEY = "f2cwxn35cxyoq8723c78wnvy"
PRODUCTION_GCM_RECEIVE_URL = "https://www.repunch.com/gcm/receive/"
PRODUCTION_GCM_RECEIVE_KEY = "sikxuuq348o75c7seoryt"

COMET_RECEIVE_URL_DELIMETER = "<<COMET_RECEIVE_URL>>"
COMET_RECEIVE_KEY_DELIMETER = "<<COMET_RECEIVE_KEY>>"
GCM_RECEIVE_URL_DELIMETER = "<<GCM_RECEIVE_URL>>"
GCM_RECEIVE_KEY_DELIMETER = "<<GCM_RECEIVE_KEY>>"

SCRIPT_DESCRIPTION = "Uses the master cloud code to deploy to the Production or Development Server."

COMMAND_DEPLOY = "deploy"
TARGET_DEV = "dev"
TARGET_PROD = "prod"

### Code starts here
parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
parser.add_argument("command", type=str, choices=[COMMAND_DEPLOY, ], help="Enter a parse command")
parser.add_argument("target", type=str, choices=[TARGET_DEV, TARGET_PROD], help="Enter the target code to apply the command")
parser.add_argument("-o", "--option", type=str, help="See parse help for possible command options")

args = parser.parse_args()
command, target, option = args.command, args.target, args.option

if command == COMMAND_DEPLOY:
    # open the master cloud code and the corresponding target cloud code
    if target == TARGET_DEV:
        target_dir = "./development/"
        comet_receive_url = DEVELOPMENT_COMET_RECEIVE_URL
        comet_receive_key = DEVELOPMENT_COMET_RECEIVE_KEY
        gcm_receive_url = DEVELOPMENT_GCM_RECEIVE_URL
        gcm_receive_key = DEVELOPMENT_GCM_RECEIVE_KEY
        
    elif target == TARGET_PROD:
        target_dir = "./production/"
        comet_receive_url = PRODUCTION_COMET_RECEIVE_URL
        comet_receive_key = PRODUCTION_COMET_RECEIVE_KEY
        gcm_receive_url = PRODUCTION_GCM_RECEIVE_URL
        gcm_receive_key = PRODUCTION_GCM_RECEIVE_KEY
        
    target_file = target_dir + "cloud/main.js"
    
    with open("./master/cloud/main.js", "r") as master,\
        open(target_file, "w+") as slave:
        print "Reading the master code..."
        master_code = master.read()
        
        print "Replacing COMET_RECEIVE_URL..."
        master_code = master_code.replace(COMET_RECEIVE_URL_DELIMETER, comet_receive_url)
        
        print "Replacing COMET_RECEIVE_KEY..."
        master_code = master_code.replace(COMET_RECEIVE_KEY_DELIMETER, comet_receive_key)
        
        print "Replacing GCM_RECEIVE_URL..."
        master_code = master_code.replace(GCM_RECEIVE_URL_DELIMETER, gcm_receive_url)
        
        print "Replacing GCM_RECEIVE_KEY..."
        master_code = master_code.replace(GCM_RECEIVE_KEY_DELIMETER, gcm_receive_key)
        
        print "Writing to %s..." % (target_file, )
        slave.write(master_code)
        
    # this must be called outside the with block to prevent io conflicts
    print "Deploying to %s..." % (target, )
    os.chdir(target_dir)
    if option:
        subprocess.call(shlex.split("parse deploy " + option))
    else:
        subprocess.call(shlex.split("parse deploy"))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
