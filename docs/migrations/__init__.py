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
    
    This assigns a new StoreLocation to the store_locations aray of pointers of each store.
    All existing Punches are also assigned the newly created StoreLocation's id.
    All existing RedeemRewards are also assigned the newly created StoreLocation's id.
    
    WARNING! Assumes this assumes that # Stores < 1000 and that each store
    has less than 1000 punches/redeemRewards in their respective relations.
    """
    for i, store in enumerate(Store.objects().filter(limit=999)):
    
        if store.store_locations: # just in case we re-run this script
            store_location = store.store_locations[0]
            
        else: # empty or None
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
            store.store_locations = [store_location]
            store.update()
        
        # update all the punches for this store
        punches = store.get("punches", order="createdAt", limit=1000)
        if punches:
            for punch in punches:
                if not punch.store_location_id:
                    punch.store_location_id = store_location.objectId
                    punch.update()
                
        # update all the redeemRewards for this store
        redeem_rewards = store.get("redeemRewards", order="createdAt", limit=1000)
        if redeem_rewards:
            for rr in redeem_rewards:
                if not rr.store_location_id:
                    rr.store_location_id = store_location.objectId
                    rr.update()
        
        print "Updated Store #" + str(i) + ": " + store.objectId
        
        
        
    
