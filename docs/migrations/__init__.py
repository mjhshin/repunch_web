"""
Database migration transcripts.
""" 

from parse.apps.patrons.models import Patron, PunchCode, PatronStore

def rename_punchcode_username_to_userid():
    """
    PunchCode username column changed to user_id.
    WARNING! Assumes this assumes that # Patrons < 1000.
    """
    for acc in Account.objects().filter(Patron__ne=None,
        include="Patron", limit=1000):
        pc = PunchCode.objects().get(punch_code=acc.patron.punch_code)
        pc.user_id = acc.objectId
        pc.update()
        print "Updated PunchCode " + acc.patron.punch_code
