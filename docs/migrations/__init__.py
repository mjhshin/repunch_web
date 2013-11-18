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

def add_punch_code_to_patronstore(delete_if_nullpatron=True):
    """
    Added punch_code column to PatronStore class.
    WARNING! Assumes this assumes that # PatronStores < 1000.
    """
    for ps in PatronStore.objects().filter(include="Patron",
        limit=1000):
        if ps.get("patron"):
            ps.punch_code = ps.patron.punch_code
            ps.update()
            print "Updated PatronStore " + ps.objectId
        else:
            if delete_if_nullpatron:
                ps.delete()
            print "PatronStore %s has a null patron" % (ps.objectId,)
