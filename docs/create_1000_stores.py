"""
As the filename states. This script will create 1000 valid 
Accounts (Users), Stores, Settings, and Subscriptions.
"""

from libs.repunch import rputils

from parse.utils import parse, create_png
from parse.apps.accounts.models import Account
from parse.apps.stores.models import Settings, Subscription, Store

def _gen_phone_number(i):
    """
    Returns a phone number generated from i with the format:
        (xxx) xxx-xxxx
    """
    return "(" + str(i%1000).zfill(3) + ") " +\
        str(i%1000).zfill(3) + "-" + str(i%10000).zfill(4)

def create():
    """
    This will store the objectIds for all created objects 
    in csv format: account,store,settings,subscription|...repeat
    """
    with open("1000_stores.txt", "a") as fd:
        for i in range(1, 1001):
            name = "store" + str(i)
            # create the Settings
            settings = Settings.objects().create()
            
            # create the Subscription
            subscription = Subscription.objects().create(first_name=\
                name, last_name=name, zip=str(10100+i))
                
            # create the store
            store = Store.objects().create(\
                active=True, store_name=name, street=name+" street",
                zip=str(10100+i), first_name=name, 
                last_name=name, phone_number=_gen_phone_number(i), 
                store_description=name, store_avatar="df9fbd9f-"+\
                    "8dfc-44d3-838b-6a5f2aebab33-showcasepic1png",
                punches_facebook=1, hours=\
                    [{"close_time":"1930","day":1,"open_time":"1000"},
                    {"close_time":"1930","day":2,"open_time":"1000"},
                    {"close_time":"1930","day":3,"open_time":"1000"},
                    {"close_time":"1930","day":4,"open_time":"1000"},
                    {"close_time":"1930","day":5,"open_time":"1000"},
                    {"close_time":"1930","day":6,"open_time":"1000"},
                    {"close_time":"1930","day":7,"open_time":"1000"}],
                rewards=\
                    [ {"reward_name": "reward #1", "description":\
                        "The first reward", "punches": 10, 
                        "redemption_count": 0, "reward_id": 0}, 
                     {"reward_name": "reward #2", "description":\
                        "The second reward", "punches": 15, 
                        "redemption_count": 0, "reward_id": 1}, 
                     {"reward_name": "reward #3", "description":\
                        "The third reward", "punches": 25, 
                        "redemption_count": 0, "reward_id": 2}, ],
                categories=\
                    [{"alias":"menscloth","name":"Men's Clothing"},],
                Subscription=subscription.objectId,
                Settings=settings.objectId)
            store.store_timezone = rputils.get_timezone(10100+i).zone
            map_data = rputils.get_map_data(str(10100+i))
            store.set("coordinates", map_data.get("coordinates"))
            store.set("neighborhood", 
                store.get_best_fit_neighborhood(\
                    map_data.get("neighborhood")))
            store.update()
            
            # create the account
            email=name+"@"+name+".com"
            account = Account.objects().create(username=email, 
                password=name, email=email, 
                Store=store.objectId)
            
            # update the pointers
            settings.Store = store.objectId
            settings.update()
            subscription.Store = store.objectId
            subscription.update()
            
            # record the objectIds
            fd.write(account.objectId+","+store.objectId+","+\
                settings.objectId+","+subscription.objectId+"|")
           
            print "created store #" + str(i) + " " + store.objectId

def delete():
    """ 
    delete the created objects 
    csv format: account,store,settings,subscription|...repeat
    """
    with open("1000_stores.txt", "r") as fd:
        record = fd.read()
        
    for i, data in enumerate(record.split("|")):
        print "deleting store #" + str(i)
        data = data.split(",")
        parse("DELETE", "classes/_User/" + data[0])
        parse("DELETE", "classes/Store/" + data[1])
        parse("DELETE", "classes/Settings/" + data[2])
        parse("DELETE", "classes/Subscription/" + data[3])
        
def update():
    """
    Updates the city, country, and state of created stores.
    """
    with open("1000_stores.txt", "r") as fd:
        record = fd.read()
        
    for i, data in enumerate(record.split("|")):
        data = data.split(",")
        store = Store.objects().get(objectId=data[1])
        store.set("city", "City " + str(i+1)) 
        store.set("country", "US") 
        store.set("state", "NY") 
        full_address = " ".join(\
            store.get_full_address().split(", "))
        map_data = rputils.get_map_data(store.zip)
        store.set("coordinates", map_data.get("coordinates"))
        store.set("neighborhood", store.get_best_fit_neighborhood(\
            map_data.get("neighborhood")))
            
        # create a png for each 1
        res =\
            create_png("/home/vestrel00/Pictures/wallpapers/test.png")
        if res and 'error' not in res:
            store.store_avatar = res.get('name')
        else:
            print "Error in creating png for store: " + store.objectId
            
        if store.update():
            print "Updated store #" + str(i+1)
        else:
            print "Error updating store: " + store.objectId
        
if __name__ == "__main__":
    create()
    # delete()
