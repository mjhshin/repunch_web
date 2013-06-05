"""
Parse equivalence of Django apps.stores.models
""" 
from datetime import datetime
from importlib import import_module
import paypalrestsdk

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
        self.active_users = data.get('active_users', 0)
        self.store_timezone = data.get('store_timezone', TIME_ZONE) 
        self.punches_facebook = data.get("punches_facebook")  
   
        self.Subscription = data.get("Subscription")
        self.Settings = data.get("Settings")

        self.Patrons_ = "Patron"
        self.Rewards_ = "Reward"
        self.Invoice_ = "Invoice"
        self.Employees_ = "Employee"
        self.Hours_ = "Hours"
        
        super(Store, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Patron":
            return getattr(import_module('parse.apps.patrons.models'),
                                className)
        elif className == "Settings":
            return Settings
        elif className == "Hours":
            return Hours
        elif className == "Invoice":
            return Invoice
        elif className == "Subscription":
            return Subscription
        elif className == "Employee":
            return getattr(import_module('parse.apps.employees.models'), className)
        elif className == "Reward":
            return getattr(import_module('parse.apps.rewards.models'),
                                className)

class Hours(ParseObject):
    """ Equivalence class of apps.stores.models.Hours """

    def __init__(self, **data):
        self.days = data.get('days')
        self.open = data.get('open')
        self.close = data.get('close')
        self.list_order = data.get('list_order')

        self.Store = data.get("Store")

        super(Hours, self).__init__(False, **data)

    def get_class(self, className):
        if className == "Store":
            return Store

class Invoice(ParseObject):
    """ Equivalence class of apps.accounts.models.Invoice """
    def __init__(self, **data):
        self.date_charged = data.get('date_charged')
        self.status = data.get('status')
        self.response = data.get('response')
        self.response_code = data.get('response_code')
        self.auth_code = data.get('auth_code')
        self.avs_response = data.get('avs_response')
        self.trans_id = data.get('trans_id')
        self.amount = data.get('amount')

        self.Store = data.get('Store')
        
        super(Invoice, self).__init__(False, **data)
        
    def get_class(self, className):
        if className == "Store":
            return Store
    
class Subscription(ParseObject):
    """ Equivalence class of apps.accounts.models.Subscription """
    def __init__(self, **data):
        self.status = data.get('status', ACTIVE)
        # stores the level in sub_type
        self.subscriptionType = data.get('subscriptionType', 0)
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.cc_number = data.get('cc_number')
        self.cc_expiration_month = data.get('cc_expiration_month')
        self.cc_expiration_year = data.get('cc_expiration_year')
        self.address = data.get('address')
        self.city = data.get('city')
        self.state = data.get('state')
        self.zip = data.get('zip')
        self.country = data.get('country')
        self.ppid = data.get('ppid')
        self.ppvalid = data.get('ppvalid')

        super(Subscription, self).__init__(False, **data)
    
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
	           "expire_month": self.cc_expiration_month,
	           "expire_year": self.cc_expiration_year,
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
            self.ppvalid = credit_card.valid_until[:10]
            self.update()
            return True
        else:
            print "Error while creating CreditCard:"
            # raise Exception(credit_card.error)
            # TODO does not check if information is correct
            # only if the fields are in correct format!
            raise Exception("Incorrect credit card information.")
            
        return False
        

    def charge_cc(self):
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
              		"total": sub_type[self.get('subscriptionType')].get('monthly_cost'),
              		"currency": "USD" },
                "description": "Recurring monthly subscription from repunch.com." 
                }] })

        if payment.create():
            invoice = Invoice()
            invoice.Store = Store.objects().get(Subscription=\
                                self.objectId).objectId
            invoice.date_charged = datetime.now()
            invoice.response_code = payment.id
            invoice.status = payment.state
            if invoice.status == 'approved':
	            invoice.trans_id = payment.transactions[0].related_resources[0].sale.id

            invoice.create()
            return invoice
        else:
            print "Error while creating payment:"
            # TODO Might want to charge curtomer 1 dollar to verify
            # account if store_cc fails to do so
            raise Exception("Something went wrong, "+\
                            "please make sure that you have the"+\
                            " correct credit card information.")
		
        return None


class Settings(ParseObject):
    """ Equivalence class of apps.accounts.models.Settings """
    def __init__(self, **data):
        self.punches_customer = data.get("punches_customer")
        self.punches_employee = data.get("punches_employee") 
        self.retailer_id = data.get("retailer_id")

        super(Settings, self).__init__(False, **data)


"""
class SubscriptionType(ParseObject):
    # Equivalence class of apps.accounts.models.SubscriptionType
    def __init__(self, **data):
        self.name = data.get('name', FREE)
        self.description = data.get('description')
        self.monthly_cost = data.get('monthly_cost', 0)
        # use UNLIMITED below for heavywight type
        self.max_users = data.get('max_users', 50)
        self.max_messages = data.get('max_messages', 1)
        self.status = data.get('status', ACTIVE)

        super(SubscriptionType, self).__init__(False, **data)
"""
 
