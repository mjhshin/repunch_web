"""
Parse equivalence of Django apps.accounts.models
"""
from datetime import datetime
from django.contrib.auth.hashers import make_password
import paypalrestsdk

from repunch.settings import PAYPAL_CLIENT_SECRET,\
PAYPAL_CLIENT_SECRET, PAYPAL_MODE, PAYPAL_CLIENT_ID
from libs.repunch.rpccutils import get_cc_type
from parse.core.models import ParseObject
from parse.utils import parse

class Account(ParseObject):
    """ Equivalence class of apps.accounts.models.Account 
        This account is special in that it is the model for
        Parse.User
    """
    def __init__(self, data={}):
        super(Account, self).__init__()
        self.objectId = data.get('objectId')
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.phone = data.get('phone')
        self.is_active = data.get('is_active', True)
        self.is_staff = data.get('is_staff', False)
        self.is_superuser = data.get('is_superuser', False)
        self.sessionToken = data.get('sessionToken')

        self.Account = data.get('Account')
        self.Store = data.get('Store')

    def path(self):
        return "users"

    def set_password(self, new_pass):
        """ sets the password to a hashed new_pass """
        self.password = make_password(new_pass)

    def get_settings(self):
        # TODO
        return None
        
    def get_sents_available(self):
        """
        returns how many messages can be sent this month
        """
        # TODO
        return None
    
    def is_free(self):
        # TODO
        return True

    def upgrade(self):
        # TODO
        return False

class Invoice(ParseObject):
    """ Equivalence class of apps.accounts.models.Subscription """
    def __init__(self, data={}):
        super(Invoice, self).__init__()
        self.objectId = data.get('objectId')
        self.charge_date = data.get('charge_date')
        self.status = data.get('status')
        self.response = data.get('response')
        self.response_code = data.get('response_code')
        self.auth_code = data.get('auth_code')
        self.avs_response = data.get('avs_response')
        self.trans_id = data.get('trans_id')
        self.amount = data.get('amount')

        self.Account = data.get('Account')
    
    
class Subscription(ParseObject):
    """ Equivalence class of apps.accounts.models.Subscription """
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    ERROR = "Billing Error"
    def __init__(self, data={}):
        super(Subscription, self).__init__()
        self.objectId = data.get('objectId')
        self.status = data.get('status')
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

        self.SubscriptionType = data.get('SubscriptionType')
    
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
            self.update();
            return True
        else:
            print("Error while creating CreditCard:")

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
              		"total": self.type.monthly_cost, # TODO
              		"currency": "USD" },
                "description": "Recurring monthly subscription from repunch.com." 
                }] })

        if payment.create():
            invoice = Invoice()
            invoice.Account = self.objectId
            invoice.charge_date = datetime.now()
            invoice.response_code = payment.id
            invoice.status = payment.state
            if invoice.status == 'approved':
	            invoice.trans_id = payment.transactions[0].related_resources[0].sale.id

            invoice.save()
            return invoice
        else:
            print("Error while creating payment:")
            raise Exception(payment.error)
		
        return None

class SubscriptionType(ParseObject):
    """ Equivalence class of apps.accounts.models.SubscriptionType """
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'

    def __init__(self, data={}):
        super(SubscriptionType, self).__init__()
        self.objectId = data.get('objectId')
        self.name = data.get('name')
        self.description = data.get('description')
        self.monthly_cost = data.get('monthly_cost', 0)
        self.max_users = data.get('max_users', 0)
        self.max_messages = data.get('max_messages', 0)
        self.level = data.get('level', 0)
        self.status = data.get('status', ACTIVE)



        
        
