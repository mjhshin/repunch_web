"""
Tests for punch.
"""

from parse.utils import cloud_call
from cloud_code.tests import CloudCodeTest
from parse.apps.accounts.models import Account

# This User exists solely for testing CloudCode.
# It must have a Store and Patron pointers.
ACCOUNT_EMAIL = "cloudcode@repunch.com"

def test_punch():
    """
    This first deletes all the PatronStores in the Store's PatronStore relation.
    """
    account = Account.objects().get(email=ACCOUNT_EMAIL,
        include="Patron,Store")
    patron = account.patron
    store = account.store
    
    if store.get("patronStores"):
        for ps in store.patronStores:
            ps.delete()
        
    store.patronStores = None
    
    test = CloudCodeTest("PUNCH", [
        {'test_name': ""},
    ])
