"""
Parse equivalence of Django apps.stores.models
""" 
from importlib import import_module
from dateutil import parser
import string, random

from parse.utils import parse, title
from parse.apps.accounts import sub_type
from libs.paypal import store_cc, charge_cc
from parse.core.models import ParseObject
from repunch.settings import TIME_ZONE
from libs.repunch import rputils
from parse.apps.stores import ACCESS_ADMIN, ACCESS_PUNCHREDEEM,\
ACCESS_NONE

DAYS = ((1, 'Sunday'),
		(2, 'Monday'),
        (3, 'Tuesday'),
        (4, 'Wednesday'),
        (5, 'Thursday'),
        (6, 'Friday'),
        (7, 'Saturday'))

SHORT_DAYS = ((1, 'Sun'),
		(2, 'Mon'),
        (3, 'Tues'),
        (4, 'Wed'),
        (5, 'Thurs'),
        (6, 'Fri'),
        (7, 'Sat'))

class Store(ParseObject):
    """ Equivalence class of apps.stores.models.Store """
    def __init__(self, **data):
        self.active = data.get('active', False)
        # the owner_id is the objectId of the original account that 
        # created this object at signup
        self.owner_id = data.get("owner_id")
        self.store_name = data.get('store_name')
        self.street = data.get("street")
        self.city = data.get('city')
        self.state = data.get('state')
        self.zip = data.get('zip')
        self.country = data.get('country')
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.phone_number = data.get('phone_number')
        self.store_description = data.get('store_description')
        self.store_avatar = data.get('store_avatar')
        self.store_timezone = data.get('store_timezone', TIME_ZONE) 
        self.neighborhood = data.get('neighborhood')
        self.cross_streets = data.get('cross_streets')
        # GeoPoint [latitude, longtitude]
        self.coordinates = data.get('coordinates')
        
        self.punches_facebook = data.get("punches_facebook", 1)  

        # [{"day":1,"open_time":"0900","close_time":"2200"}, 
        #    ... up to day 7]
        self.hours = data.get("hours")
        # [{"reward_name":"Free bottle of wine", "description":
        # "Must be under $25 in value",
        # "punches":10,"redemption_count":0, reward_id:0},]
        self.rewards = data.get("rewards")
        # [{"alias":"bakery","name":"Bakeries"},
        # {"alias":"coffee","name":"Coffee & Tea"}]
        self.categories = data.get('categories')

        self.Subscription = data.get("Subscription")
        self.Settings = data.get("Settings")

        self.Punches_ = "Punch"
        self.PatronStores_ = "PatronStore"
        self.Employees_ = "Employee"
        self.FacebookPosts_ = "FacebookPost"
        self.SentMessages_ = "Message"
        self.ReceivedMessages_ = "Message"
        self.RedeemRewards_ = "RedeemReward"
        
        super(Store, self).__init__(False, **data)
     
    def update(self):
        """
        Capitalize certain strings before saving to parse.
        """
        self.store_name = title(self.store_name)       
        self.street = title(self.street)
        self.city = title(self.city)
        if self.state:
            self.state = self.state.upper()
        
        data = self._get_formatted_data()
        res = parse("PUT", self.path() + "/" + self.objectId, data)
        if res and "error" not in res:
            self.update_locally(res, False)
            return True

        return False
        
    def get_owner_fullname(self):
        return self.first_name.capitalize()+\
                " " + self.last_name.capitalize()
                
    def get_access_level(self, account):
        """ Returns the access level of the given account 
            ACCESS_ADMIN = {"read": True, "write": True}
            ACCESS_PUNCHREDEEM = {"read": True}
            ACCESS_NONE = /not in ACL/
        """
        if account.objectId in self.ACL:
            acl = self.ACL[account.objectId]
            if acl.get("read") and acl.get("write"):
                return ACCESS_ADMIN
            elif acl.get("read"):
                return ACCESS_PUNCHREDEEM
        return ACCESS_NONE
            
    def is_admin(self, account):
        """ Returns true if the account has full admin access """
        return self.get_access_level(account) == ACCESS_ADMIN
        
    def is_owner(self, account):
        """ Returns true if the account is the owner of the store """
        return self.owner_id == account.objectId
        
    def has_access(self, account):
        """ 
        Returns true if the account does not have an ACL = ACCESS_NONE
        """
        return self.get_access_level(account)[1] > ACCESS_NONE[1]
   
    def get_full_address(self):
        """
        Returns street, city, state, zip, country
        """
        full_address = ''
        if self.street:
            full_address += self.street + ", "
        if self.city:
            full_address += self.city + ", "
        if self.state:
            full_address += self.state + ", "
        if self.zip:
            full_address += self.zip + ", "
        if self.country:
            full_address += self.country
        return full_address
            
    def get_best_fit_neighborhood(self, exact_neighborhood):
        """
        neighborhood of exact address may sometimes be incorrect.
        exact_neighborhood is the neighborhood of the exact address.
        
        e.g. http://maps.googleapis.com/maps/api/geocode/json?
                address=155+water+st+brooklyn+ny&sensor=false
                
            outputs neighborhood as Vinegar Hill instead of Dumbo
        """
        
        # 1 above e.g. 155 water st -> 156 water st
        neighborhoods = [exact_neighborhood]
        full_address = " ".join(self.get_full_address().split(", "))
        pieces = full_address.split(" ")
        st_num = pieces[0]
        if st_num.isdigit():
            pieces[0] = str(int(st_num)+1)
            neighborhoods.append(rputils.get_map_data(\
                " ".join(pieces)).get("neighborhood"))
            pieces = full_address.split(" ")
            st_num = pieces[0]
            
        # 1 below e.g. 155 water st -> 154 water st
        pieces = full_address.split(" ")
        st_num = pieces[0]
        if st_num.isdigit():
            pieces[0] = str(int(st_num)-1)
            neighborhoods.append(rputils.get_map_data(\
                " ".join(pieces)).get("neighborhood"))
            pieces = full_address.split(" ")
            st_num = pieces[0]
            
        # now choose the best fit
        max_count, best_fit = 0, None
        for n in neighborhoods:
            count = neighborhoods.count(n)
            if count > max_count:
                max_count = count
                best_fit = n
        
        return best_fit

    def get_class(self, className):
        if className in ("PatronStore", "FacebookPost") :
            return getattr(import_module('parse.apps.patrons.models'), className)
        elif className == "Settings":
            return Settings
        elif className == "Subscription":
            return Subscription
        elif className in ("Punch", "RedeemReward"):
            return getattr(import_module('parse.apps.rewards.models'), className)
        elif className == "Employee":
            return getattr(import_module('parse.apps.employees.models'), className)
        elif className == "Message":
            return getattr(import_module('parse.apps.messages.models'), className)

class Invoice(ParseObject):
    """ Equivalence class of apps.accounts.models.Invoice """
    def __init__(self, **data):
        # use type to distinguish between different types of payments
        # monthly, smartphone
        self.type = data.get("type")
        self.state = data.get('state')
        self.payment_id = data.get('payment_id')
        self.sale_id = data.get('sale_id')
        self.total = data.get('total')
        
        super(Invoice, self).__init__(False, **data)
        
    def as_ul(self):
        """
        Returns this invoice object as an html ul.
        """
        span = '<span style="color:#545454;font-weight:bold;">'
        return "<ul>" +\
            "<li>"+span+"Invoice Type:</span> " + str(self.type) +\
                "</li>" +\
            "<li>"+span+"State:</span> " + str(self.state) +\
                "</li>" +\
            "<li>"+span+"Payment Id:</span> " +\
                str(self.payment_id) + "</li>" +\
            "<li>"+span+"Sale Id:</span> " + str(self.sale_id) +\
                "</li>" +\
            "<li>"+span+"Total (USD):</span> $" + str(self.total) +\
                "</li></ul>"
        
    
class Subscription(ParseObject):
    """ Equivalence class of apps.accounts.models.Subscription """
    def __init__(self, **data):
        # stores the level in sub_type
        self.subscriptionType = data.get('subscriptionType', 0)
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        # only store last 4 digits
        self.cc_number = data.get('cc_number')
        self.date_cc_expiration = data.get('date_cc_expiration')
        self.address = data.get('address')
        self.city = data.get('city')
        self.state = data.get('state')
        self.zip = data.get('zip')
        self.country = data.get('country')
        # credit card id for paypal
        # note that the objectId of this object will be used as the
        # payer_id for paypal since it is guaranteed to be unique
        self.pp_cc_id = data.get('pp_cc_id')
        self.date_pp_valid = data.get('date_pp_valid')
        
        # used when the user passes the user limit!!
        # MUST be set back to None if not in use!!!!
        self.date_passed_user_limit =\
            data.get("date_passed_user_limit")
            
        # like date_passed_user_limit but used for the case where
        # a stored paypal cc failed to be charged because invalid
        self.date_charge_failed =\
            data.get("date_charge_failed")
        
        # use to bill monthly! ONLY USE for determining when to charge
        # monthly bill for premium accounts- not for smartphones or
        # other services!
        self.date_last_billed = data.get("date_last_billed")
        
        self.Store = data.get("Store")
        self.Invoices_ = "Invoice"

        super(Subscription, self).__init__(False, **data)
  
    
    def get_class(self, className):
        if className == "Invoice":
            return Invoice
        elif className == "Store":
            return Store
    
    def get_full_address(self):
        """
        Returns address, city, state, zip, country
        """
        return self.address + ", " + self.city  + ", " +\
            self.state + ", " + self.zip  + ", " + self.country
        
    def _trim_cc_number(self):
        """ make sure to call this before saving this object """
        if self.cc_number and len(self.cc_number) > 4:
            self.cc_number = self.cc_number[-4:]
        
    def update(self):
        """ 
        Override to trim the cc_number before storing
        """
        # get the formated data to be put in the request
        self._trim_cc_number()
        data = self._get_formatted_data()

        res = parse("PUT", self.path() + "/" + self.objectId, data)
        if res and "error" not in res:
            self.update_locally(res, True)
            return True

        return False

    def create(self):
        """ 
        Override to trim the cc_number before storing
        """
        data = self._get_formatted_data()
        self._trim_cc_number()
        res = parse('POST', self.path(), data)
        if res and "error" not in res:
            self.update_locally(res, True)
            return True
        
        return False
    
    def store_cc(self, cc_number, cvv2):
        """ store credit card info. returns True if successful """
        # TODO verify credit card cvv2 and expiration date ?!
        try:
            res = store_cc(self, cc_number, cvv2)
        except Exception as e: 
            return False
        else:
            # something went wrong though this should never occur
            if not res.ok:
                return False
                
            res = res.json()
            self.pp_cc_id = res['id']
            self.date_pp_valid = parser.parse(res['valid_until'])
            self.update()
            return True       

    def charge_cc(self, total, description, type):
        """
        For charging for monthly non-free membership fees,
        total: sub_type[self.get('subscriptionType')].\
                                                get('monthly_cost')
        description: "Recurring monthly subscription "+\
                        from repunch.com." 
                        
        Returns the Invoice if success. Or None if not.
        """
        res = None
        try:
            res = charge_cc(self, total, description)
        # something went wrong
        except Exception as e: 
            return None
        else:
            # maybe because of invalid ccv and/or expiration date
            # or insufficient funds or if the credit card was refused
            # for some other reason
            if not res.ok:
                return None
                
            res = res.json()
            invoice = Invoice(
                state = res['state'],
                payment_id = res['id'],
                total = total,
                type = type,
            )
            if invoice.state == 'approved':
                try:
	                invoice.sale_id =\
	                    res['transactions'][0]['related_resources'][0]['sale']['id']
                except Exception:
                    pass # key error or something
            invoice.create()
            self.add_relation("Invoices_", [invoice.objectId])
            return invoice
            
class Settings(ParseObject):
    """ Equivalence class of apps.accounts.models.Settings """
    def __init__(self, **data):
        self.punches_employee = data.get("punches_employee", 5) 
        self.retailer_pin = data.get("retailer_pin", 
            Settings.generate_id())

        self.Store = data.get('Store')

        super(Settings, self).__init__(False, **data)
    
    @staticmethod
    def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
        """ Returns a new retailer_id """
        gid = ''.join(random.choice(chars) for x in range(size))

        #make sure this is a unique ID
        if Settings.objects().count(retailer_pin=gid) == 0:
            return gid

        return generate_id()

    def get_class(self, className):
        if className == "Store":
            return Store

