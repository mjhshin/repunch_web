"""
Refer to http://pymotw.com/2/imaplib/ for further development.
"""

import imaplib, re
from dateutil.parser import parse
from dateutil.tz import tzutc
from django.utils import timezone

from repunch.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

class Mail(object):
    """
    Small wrapper around the imap module.
    """
    
    SENT_MAILBOX = "[Gmail]/Sent Mail"
    HEADER_DATE_RE = re.compile(r"Date: (?P<date>.*) -", re.DOTALL)
    
    def __init__(self, username=EMAIL_HOST_USER,
        password=EMAIL_HOST_PASSWORD, hostname="imap.gmail.com"):
        """
        Open the connection to the email server.
        For gmail, hostname is imap.gmail.com.
        """
        self.conn = imaplib.IMAP4_SSL(hostname, 993)
        self.conn.login(username, password)
        
    def get_mailboxes(self):
        """
        Returns a list of mailbox names.
        """
        return [row.split('"/"')[1] for row in self.conn.list()[1]]
        
    def select_mailbox(self, mailbox_name, readonly=True):
        """ Set the currently opened mailbox """
        return self.conn.select(mailbox_name, readonly=readonly)
        
    def select_sent_mailbox(self, readonly=True):
        """ Set the currently opened mailbox to sent mail """
        return self.conn.select(Mail.SENT_MAILBOX, readonly=readonly)
        
    def search_by_subject(self, subject):
        """ 
        Matches the subject with a subject of one of the mails
        in the currently selected mailbox if it exists. 
        Returns the list of ids of all matching emails as strings
        in ascending order.
        """
        ids = self.conn.search(None, '(SUBJECT "'+\
            subject + '")')[1][0]
        if ids:
            ids = [int(i) for i in ids.split(" ")]
            ids.sort()
        return ids
        
    def fetch_date(self, ids):
        """ Fetches the date of the email with the given id """
        headers = self.conn.fetch(ids, '(BODY.PEEK[HEADER])')[1][0][1]
        return timezone.make_aware(parse(Mail.HEADER_DATE_RE.search(\
            headers).group("date")), tzutc())
        
    def logout(self):
        self.conn.logout()
        
    
