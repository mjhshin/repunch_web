"""
Tests for add_patronstore and delete_patronstore.
"""

from parse.utils import cloud_call

# The patron store created from the below are temporary.
# This means it gets deleted.
PATRON_ID = 
STORE_ID = 

def test_add_delete_patron_store():
    """
    This test also calls punch.
    """
    results = []
    parts = [
        {'test_name': "Non-existent PatronStore is created"},
        {'test_name': "PatronStore is add to Patron's PatronStores relation"},
        {'test_name': "PatronStore is add to Store's PatronStores relation"},
    ]
    section = {
        "section_name": "ADD_PATRONSTORE",
        "parts": parts,
    }
    results.append(section)
    
    
    
    
    # END OF ALL TESTS - cleanup
    return results
