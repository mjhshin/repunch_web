"""
Database migration transcripts.
""" 

from parse.apps.accounts.models import Account
from parse.apps.patrons.models import Patron, PunchCode, PatronStore
from parse.apps.stores.models import Store, StoreLocation
from parse.apps.rewards.models import Punch

def rename_punchcode_username_to_userid():
    """
    PunchCode username column changed to user_id.
    WARNING! Assumes this assumes that # Patrons < 1000.
    """
    for acc in Account.objects().filter(Patron__ne=None,
        include="Patron", limit=999):
        pc = PunchCode.objects().get(punch_code=acc.patron.punch_code)
        pc.user_id = acc.objectId
        pc.update()
        print "Updated PunchCode " + acc.patron.punch_code
        
def supported_chain_stores():
    """
    Created the StoreLocation class, which contains Store location
    information. A Store may have multiple StoreLocations.
    Punches also now have store_location_id.
    
    This adds a new StoreLocation to the StoreLocations relation of each store.
    All existing Punches are also assigned the newly created StoreLocation's id.
    
    WARNING! Assumes this assumes that # Stores < 1000 and that each store
    has less than 1000 punches in their Punches relation.
    """
    for i, store in enumerate(Store.objects().filter(limit=999)):
        store_location = StoreLocation.objects().create(**{
            "street": store.street,
            "city": store.city,
            "state": store.state,
            "zip": store.zip,
            "country": store.country,
            "phone_number": store.phone_number,
            "store_timezone": store.store_timezone,
            "neighborhood": store.neighborhood,
            "coordinates": store.coordinates,
            "hours": store.hours,
            "store_avatar": store.store_avatar,
            "Store": store.objectId,
        })
        store.add_relation("StoreLocations_", [store_location.objectId])
        
        # update all the punches for this store
        for punch in store.get("punches", order="createdAt", limit=1000):
            punch.store_location_id = store_location.objectId
        
        print "Updated Store #" + str(i) + ": " + store.objectId
        
        
        
    
