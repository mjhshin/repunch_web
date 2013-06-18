"""
Parse equivalence of Django apps.stores.models
""" 
from datetime import datetime
from importlib import import_module
import paypalrestsdk

from parse.utils import parse
from parse.apps.accounts import sub_type
from repunch.settings import PAYPAL_CLIENT_SECRET,\
PAYPAL_CLIENT_SECRET, PAYPAL_MODE, PAYPAL_CLIENT_ID
from libs.repunch.rpccutils import get_cc_type

from repunch.settings import TIME_ZONE
from parse.core.models import ParseObject

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
        
        self.punches_facebook = data.get("punches_facebook")  

        # [{"day":0,"open_time":"0900","close_time":"2200"}, 
        #    ... up to day 6]
        self.hours = data.get("hours")
        # [{"reward_name":"Free bottle of wine", "description":
        # "Must be under $25 in value",
        # "punches":10,"redemption_count":0},]
        self.rewards = data.get("rewards")
        # [{"alias":"bakery","name":"Bakeries"},
        # {"alias":"coffee","name":"Coffee & Tea"}]
        self.categories = data.get('categories')

        # GeoPoint TODO
        # self.coordinates = data.get('coordinates')
   
        self.Subscription = data.get("Subscription")
        self.Settings = data.get("Settings")

        self.Punches_ = "Punch"
        self.PatronStores_ = "PatronStore"
        self.Invoices_ = "Invoice"
        self.Employees_ = "Employee"
        self.FacebookPosts_ = "FacebookPost"
        self.SentMessages_ = "Message"
        self.ReceivedMessages_ = "Message"
        
        super(Store, self).__init__(False, **data)

    def get_class(self, className):
        if className in ("PatronStore", "FacebookPost") :
            return getattr(import_module('parse.apps.patrons.models'), className)
        elif className == "Settings":
            return Settings
        elif className == "Invoice":
            return Invoice
        elif className == "Subscription":
            return Subscription
        elif className == "Punch":
            return getattr(import_module('parse.apps.rewards.models'), className)
        elif className == "Employee":
            return getattr(import_module('parse.apps.employees.models'), className)
        elif className == "Message":
            return getattr(import_module('parse.apps.messages.models'), className)

class Invoice(ParseObject):
    """ Equivalence class of apps.accounts.models.Invoice """
    def __init__(self, **data):
        self.status = data.get('status')
        self.response = data.get('response')
        self.response_code = data.get('response_code')
        self.auth_code = data.get('auth_code')
        self.avs_response = data.get('avs_response')
        self.trans_id = data.get('trans_id')
        self.amount = data.get('amount')
        
        super(Invoice, self).__init__(False, **data)
        
    
class Subscription(ParseObject):
    """ Equivalence class of apps.accounts.models.Subscription """
    def __init__(self, **data):
        self.active = data.get('active', False)
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
        # ppid only thin required to save
        self.ppid = data.get('ppid')
        self.date_ppvalid = data.get('date_ppvalid')

        super(Subscription, self).__init__(False, **data)
        
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
    
    def store_cc(self, cc_number, cvv):
        """ store credit card info """
        paypalrestsdk.configure(mode=PAYPAL_MODE, 
                                client_id=PAYPAL_CLIENT_ID, 
                                client_secret=PAYPAL_CLIENT_SECRET)
		
        credit_card = paypalrestsdk.CreditCard({
	           # ###CreditCard
	           # A resource representing a credit card that can be
	           # used to fund a payment.
	           "type": get_cc_type(cc_number),
	           "number": cc_number,
	           "expire_month": self.date_cc_expiration.month,
	           "expire_year": self.date_cc_expiration.year,
	           "cvv2": cvv,
	           "first_name": self.first_name,
	           "last_name": self.last_name,
	
	            # ###Address
	            # Base Address object used as shipping or billing
	            # address in a payment. [Optional]
	           "billing_address": {
	             "line1": self.address,
	             "city": self.city,
	             "state": self.state,
	             "postal_code": self.zip,
	             "country_code": self.country }})
		
		# Make API call & get response status
		# ###Save
		# Creates the credit card as a resource
		# in the PayPal vault.
        if credit_card.create():
            self.ppid = credit_card.id
            self.date_ppvalid =\
                datetime.strptime(credit_card.valid_until[:10], 
                "%Y-%m-%d")
            self.update()
            return True
        else:
            print "Error while creating CreditCard:"
            # raise Exception(credit_card.error)
            # TODO does not check if information is correct
            # only if the fields are in correct format!
            # may go here because of non-alphanumeric inputs to name,
            
        return False
        

    def charge_cc(self, total, description):
        """
        For charging for monthly non-free membership fees,
        total: sub_type[self.get('subscriptionType')].\
                                                get('monthly_cost')
        description: "Recurring monthly subscription "+\
                        from repunch.com." 
        """
        paypalrestsdk.configure(mode=PAYPAL_MODE, 
                            client_id=PAYPAL_CLIENT_ID,
                            client_secret=PAYPAL_CLIENT_SECRET)
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
            "payment_method": "credit_card",
            "funding_instruments": [{
              	"credit_card_token": {
                	"credit_card_id": self.ppid }}]},

            "transactions": [{
                "amount": {
              		"total": total,
              		"currency": "USD" },
                "description": description
                }] })

        if payment.create():
            invoice = Invoice(amount=total)
            invoice.response_code = payment.id
            invoice.status = payment.state
            if invoice.status == 'approved':
	            invoice.trans_id = payment.transactions[0].related_resources[0].sale.id
            invoice.create()
            st = Store.objects().get(Subscription=self.objectId)
            st.add_relation("Invoices_", [invoice.objectId])
            return invoice
        else:
            # TODO Might want to charge curtomer 1 dollar to verify
            # account if store_cc fails to do so
            raise Exception(payment.error)
		
        return None


class Settings(ParseObject):
    """ Equivalence class of apps.accounts.models.Settings """
    def __init__(self, **data):
        self.punches_customer = data.get("punches_customer")
        self.punches_employee = data.get("punches_employee") 
        self.retailer_pin = data.get("retailer_pin")

        self.Store = data.get('Store')

        super(Settings, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Store":
            return Store

