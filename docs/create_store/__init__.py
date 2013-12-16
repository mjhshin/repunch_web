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

from django.utils import timezone
from random import randint
import requests

from parse.utils import create_png
from parse.apps.accounts.models import Account
from parse.apps.stores.models import Store, StoreLocation, Settings, Subscription
from repunch.settings import TIME_ZONE

DIR = "docs/create_store/"

STORE = {
    "active": True,
    "punches_facebook": 1,
    "ACL": {"*": {"read": True,"write": True}},
}
STORE_LOCATION = {
    "store_timezone": TIME_ZONE,
    "country": "US",
    "hours": [
        {"day":2,"open_time":"0900","close_time":"1700"},
        {"day":3,"open_time":"0900","close_time":"1700"},
        {"day":4,"open_time":"0900","close_time":"1700"},
        {"day":5,"open_time":"0900","close_time":"1700"},
        {"day":6,"open_time":"0900","close_time":"1700"},
    ],
}

USER_EMAIL_POSTFIX = "@repunch.com"
USER_PASSWORD = "repunch7575"

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

TMP_IMG_PATH = DIR+"tmp.png"

class RandomStoreGenerator(object):

    def __init__(self):
        with open(DIR+"addresses.txt", "r") as addrs,\
            open(DIR+"neighborhoods.txt", "r") as neighborhoods,\
            open(DIR+"store_names.txt", "r") as stores,\
            open(DIR+"image_urls.txt", "r") as images,\
            open(DIR+"owner_names.txt", "r") as owners:
            self.owners = owners.read().split("\n")
            self.addrs = addrs.read().split("\n")
            self.stores = stores.read().split("\n")
            self.neighborhoods = neighborhoods.read().split("\n")
            self.images = images.read().split("\n")
        
    def create_random_stores(self, amount):
        for i in range(amount):
            print "Creating store %s" % (str(i),) 
            # create the store
            street, city, state, zip, country, phone_number =\
                self.addrs[i].split(", ")
            first_name, last_name = self.owners[i].split(" ")
            neighborhood = self.neighborhoods[i]
            store_name = self.stores[i]
            store_i = STORE.copy()
            store_location_i = STORE_LOCATION.copy()
            
            self.get_store_location_avatar(i)
            avatar = create_png(TMP_IMG_PATH)
            while "error" in avatar:
                print "Retrying create_png"
                avatar = create_png(TMP_IMG_PATH)
            
            store_i.update({
                "store_name": store_name,
                "first_name": first_name,
                "last_name": last_name,
            })
            store_location_i.update({
                "street": street,
                "city": city,
                "state": state,
                "zip": zip,
                "neighborhood": neighborhood,
                "country": country,
                "phone_number": phone_number,
                "coordinates": self.get_random_coordinates(),
                "store_avatar": avatar.get("name"),
            })
            
            # create the store
            store = Store.objects().create(**store_i)   
    
            # create the store location
            store_location = StoreLocation(**store_location_i)
            store_location.Store = store.objectId
            store_location.update()
            
            # create the settings
            settings = Settings.objects().create(Store=store.objectId)
            
            # create the subscription
            subscription =\
                Subscription.objects().create(Store=store.objectId,
                    date_last_billed=timezone.now())
            
            # create the user
            email = first_name+str(randint(0, 99))+USER_EMAIL_POSTFIX
            email = email.lower()
            acc = Account.objects().create(\
                username=email, email=email,
                password=USER_PASSWORD, Store=store.objectId)
            if not acc.objectId:
                raise Exception("Account creation failed.")
                
            # link the store
            store.Settings = settings.objectId
            store.Subscription = subscription.objectId
            store.owner_id = acc.objectId
            store.ACL[acc.objectId] = {"read": True,"write": True}
            store.store_locations = [store_location]
            store.update()
            
    def get_store_location_avatar(self, i):
        """
        Read the image to tmp.png.
        Thanks to 
            http://stackoverflow.com/questions/13137817/
            how-to-download-image-using-requests
        """
        r = requests.get(self.images[i], stream=True)
        if r.status_code == 200:
            with open(TMP_IMG_PATH, 'wb') as fid:
                for chunk in r.iter_content():
                    fid.write(chunk)
            
    def get_random_coordinates(self):
        """
        Just pick a random lat/long in between the maximum lat/long
        """
        latitude = list(str(BASE_LAT + randint(0, RANGE_LAT)))
        longitude = list(str(BASE_LONG + randint(0, RANGE_LONG)))
        # add the decimal
        latitude.insert(2, ".")
        longitude.insert(3, ".")
        latitude = float("".join(latitude))
        longitude = float("".join(longitude))
        return [latitude, longitude]    

if __name__ == "__main__":
    generator = RandomStoreGenerator()
    generator.create_random_stores(200)
