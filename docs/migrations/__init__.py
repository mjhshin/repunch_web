"""
Database migration transcripts.
""" 

from parse.apps.patrons.models import Patron, PunchCode

def migrate_punchcode_username_userid():
    """
    PunchCode username column changed to user_id.
    """
    for acc in Account.objects().filter(Patron__ne=None, include="Patron"):
        pc = PunchCode.objects().get(punch_code=acc.patron.punch_code)
        pc.user_id = acc.objectId
        pc.update()
        print "Updated PunchCode " + acc.patron.punch_code

