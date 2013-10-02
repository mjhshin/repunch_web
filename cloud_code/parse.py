#!/usr/bin/env python

"""
Wrapper around the parse command line tool for synchronization
between production and development cloud codes.

All edits to the production and development cloud codes are ignored!
"""

import os, subprocess, shlex, re, argparse

DEVELOPMENT_COMET_RECEIVE_URL = "http://dev.repunch.com/manage/comet/receive/"
DEVELOPMENT_COMET_RECEIVE_KEY = "384ncocoacxpvgrwecwy"

PRODUCTION_COMET_RECEIVE_URL = "https://www.repunch.com/manage/comet/receive/"
PRODUCTION_COMET_RECEIVE_KEY = "f2cwxn35cxyoq8723c78wnvy"

COMET_RECEIVE_URL_DELIMETER = "<<COMET_RECEIVE_URL>>"
COMET_RECEIVE_KEY_DELIMETER = "<<COMET_RECEIVE_KEY>>"

SCRIPT_DESCRIPTION = "Uses the master cloud code to deploy to the Production or Development Server."
SLAVE_TEXT = "All changes to this file are ignored! Edit the master code instead."

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
        target_file = "./development/"
        comet_receive_url = DEVELOPMENT_COMET_RECEIVE_URL
        comet_receive_key = DEVELOPMENT_COMET_RECEIVE_KEY
        
    elif target == TARGET_PROD:
        target_file = "./production/"
        comet_receive_url = PRODUCTION_COMET_RECEIVE_URL
        comet_receive_key = PRODUCTION_COMET_RECEIVE_KEY
        
    target_file += "cloud/main.js"
    
    with open("./master/cloud/main.js", "r") as master,
        open(target_file, "w+") as slave:
        print "Reading the master code..."
        # TODO
        print "Replacing COMET_RECEIVE_URL..."
        # TODO
        print "Replacing COMET_RECEIVE_KEY..."
        # TODO
        print "Writing to %s" % (target_file, )
        # TODO
        print "Deploying to %s" % (target, )
        # TODO
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
