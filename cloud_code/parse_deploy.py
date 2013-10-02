"""
Uses the master cloud code to deploy to the Production or Development Server.

To deploy to development: python parse_deploy dev
To deploy to production: python parse_deploy prod

All edits to the production and development cloud codes are ignored!
"""

import os, sys, subprocess, shlex, re, argparse

DEVELOPMENT_COMET_RECEIVE_URL = "http://dev.repunch.com/manage/comet/receive/"
DEVELOPMENT_COMET_RECEIVE_KEY = "384ncocoacxpvgrwecwy"

PRODUCTION_COMET_RECEIVE_URL = "https://www.repunch.com/manage/comet/receive/"
PRODUCTION_COMET_RECEIVE_KEY = "f2cwxn35cxyoq8723c78wnvy"

COMET_RECEIVE_URL_DELIMETER = "<<COMET_RECEIVE_URL>>"
COMET_RECEIVE_KEY_DELIMETER = "<<COMET_RECEIVE_KEY>>"

SLAVE_TEXT = "All changes to this file are ignored! Edit the master code instead."

def deploy(argv):















if __name__ == "__main__":
    deploy(sys.argv)
