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
        with open(DIR+"addresses.txt", "r") as addr,\
            open(DIR+"owner_names.txt", "r") as own:
            self.owners = own.read().split("\n")
            self.addrs = addr.read().split("\n")
            # TODO neighborhoods
            # TODO image urls            
        
    def create_random_stores(self, amount):
        for i in range(amount):
            street, city, state, zip, country, phone_number =\
                self.addrs[i].split(", ")
            first_name, last_name = self.owners[i].split(" ")
            # TODO coordinates
            # TODO store_avatar
            # TODO neighborhood
            store_i = STORE.copy()
            store_i.update({
                "street": street,
                "city": city,
                "state": state,
                "zip": zip,
                "country": country,
                "phone_number", phone_number
                "first_name": first_name,
                "last_name": last_name,
            })
            store = Store(**store_i)   
            store.create()     
            
    def get_random_coordinates(self):
        """
        Just pick a random lat/long in between the maximum lat/long
        """
        latitude = str(BASE_LAT + randint(0, RANGE_LAT))
        longitude = str(BASE_LONG + randint(0, RANGE_LONG))
        # add the decimal
        return [latitude, longitude]    
            
        
if __name__ == "__main__":
    generator = RandomStoreGenerator()
    generator.create_random_stores(5)
