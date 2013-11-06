"""
Random NY store generator!

0) List of fake store names taken from
    
1) List of fake addresses taken from
    http://names.igopaygo.com/street/north_american_address
2) List of fake names taken from
    http://listofrandomnames.com/
3) Latitude and Longitude parameters taken from
    http://itouchmap.com/latlong.html
4) Image urls taken from google images
""" 

from random import randint

from parse.apps.accounts.models import Account
from parse.apps.stores.models import Store, Settings, Subscription
from repunch.settings import TIME_ZONE

DIR = "docs/create_store/"

STORE = {
    "active": True,
    "country": "US",
    "punches_facebook": 1,
    "store_timezone": TIME_ZONE,
    "hours": [
        {"day":2,"open_time":"0900","close_time":"1700"},
        {"day":3,"open_time":"0900","close_time":"1700"},
        {"day":4,"open_time":"0900","close_time":"1700"},
        {"day":5,"open_time":"0900","close_time":"1700"},
        {"day":6,"open_time":"0900","close_time":"1700"},
    ],
}

# Rectangular area around NY 
# format: (bottom_left, top_left, top_right, bottom_right)
# note that latitude = y-axis, longitude = x-axis
COORD_PARAM = (
    # (latitude, longitude)
    (40.617579,-74.014635),
    (40.836582,-74.014635),
    (40.836582,-73.783150),
    (40.617579,-73.783150),
)
BASE_LAT = 40617579
BASE_LONG = -74014635
RANGE_LAT = 40836582 - 40617579
RANGE_LONG = -73783150 + 74014635

class RandomStoreGenerator(object):

    def __init__(self):
        with open(DIR+"addresses.txt", "r") as addrs,\
            open(DIR+"neighborhoods.txt", "r") as neighborhoods,
            open(DIR+"store_names.txt", "r") as stores,
            open(DIR+"owner_names.txt", "r") as owners:
            self.owners = owners.read().split("\n")
            self.addrs = addrs.read().split("\n")
            self.stores = stores.read().split("\n")
            self.neighborhoods = neighborhoods.read().split("\n")
            # TODO image urls            
        
    def create_random_stores(self, amount):
        for i in range(amount):
            street, city, state, zip, country, phone_number =\
                self.addrs[i].split(", ")
            first_name, last_name = self.owners[i].split(" ")
            neighborhood = self.neighborhoods[i]
            store_name = self.stores[i]
            store_i = STORE.copy()
            store_i.update({
                "store_name": store_name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zip,
                "neighborhood": neighborhood,
                "country": country,
                "phone_number", phone_number
                "first_name": first_name,
                "last_name": last_name,
                "coordinates": self.get_random_coordinates(),
                
            })
            store = Store(**store_i)   
            store.create()    
            
            
            # TODO store_avatar 
            
    def get_random_coordinates(self):
        """
        Just pick a random lat/long in between the maximum lat/long
        """
        latitude = list(str(BASE_LAT + randint(0, RANGE_LAT)))
        longitude = list(str(BASE_LONG + randint(0, RANGE_LONG)))
        # add the decimal
        latitude = latitude.insert(2, ".")
        longitude = longitude.insert(3, ".")
        return [latitude, longitude]    

if __name__ == "__main__":
    generator = RandomStoreGenerator()
    generator.create_random_stores(5)
