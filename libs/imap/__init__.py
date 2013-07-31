"""
Refer to http://pymotw.com/2/imaplib/ for further development.
"""

import imaplib

class Mail(object):
    """
    Small wrapper around the imap module.
    """
    
    def __init__(self, username, password, hostname="imap.gmail.com"):
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
        
    def search_by_subject(self, subject):
        """ 
        Matches the subject with a subject of one of the mails
        in the currently selected mailbox if it exists. 
        Returns the list of ids of all matching emails.
        """
        return self.conn.search(None, '(SUBJECT "'+\
            subject + '")')[1]
        
    def fetch(self, id):
        """ Fetches the contents of the email with the given id """
        pass
        
    def logout(self):
        self.conn.logout()
        
    
