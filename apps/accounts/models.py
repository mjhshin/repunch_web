from django.db import models 
from django.contrib.auth.models import AbstractUser, UserManager
import datetime, paypalrestsdk, random, string

from libs.repunch import rpccutils
from apps.stores.models import Store
from libs.repunch.rpccutils import get_cc_type

class Account(AbstractUser):
	store = models.OneToOneField(Store,null=True,blank=True)
	subscription = models.OneToOneField('Subscription',null=True,blank=True)
	phone_number = models.CharField(max_length=255)

	objects = UserManager()
	
	def get_settings(self):
		results =  Settings.objects.filter(account=self)
		if results.count() == 0:
			return None
		
		return results.get();
	
	#returns how many messages can be sent this month
	def get_sents_available(self):
		from apps.messages.models import Message
		atype = self.subscription.type
		now = datetime.datetime.now()
		message_count = Message.objects.filter(date_sent__year=now.year, date_sent__month=now.month,store=self.store).count()
		return atype.max_messages-message_count
	
	def is_free(self):
		free_type = SubscriptionType.objects.filter(monthly_cost=0,status=1)
		return (self.subscription.type == free_type)
	
	def upgrade(self):
		next_level = SubscriptionType.objects.filter(level__gt=self.subscription.type.level).order_by('level');
		
		if next_level.count() > 0:
			
			self.subscription.type = next_level[0];
			self.subscription.save();
			return True
		
		return False
	
class Settings(models.Model):
	account = models.ForeignKey(Account)
	retailer_id = models.CharField(max_length=255, default="")
	punches_customer = models.IntegerField('Number of separate times a customer can receive punches per day')
	punches_employee = models.IntegerField('Number of punches allowed by an employee at one time')
	punches_facebook = models.IntegerField('Free Punch Allowance for Facebook')
	
class SubscriptionType(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	monthly_cost = models.IntegerField(default=0, blank=True)
	max_users = models.IntegerField(default=0)
	max_messages = models.IntegerField(default=0)
	level = models.IntegerField(default=0, blank=True)
	status = models.IntegerField(choices=((1,'Active'),(0,'Inactive')),default=1,max_length=255, blank=True)
	
	def __unicode__( self ):
		return self.description

class Subscription(models.Model):
	status = models.IntegerField(choices=((1,'Active'),(0,'Inactive'),(2,'Billing Error')),default=0)
	type = models.ForeignKey(SubscriptionType)
	first_name = models.CharField(max_length=255,null=True,blank=True)
	last_name = models.CharField(max_length=255,null=True,blank=True)
	cc_number = models.CharField(max_length=255,null=True,blank=True)
	cc_expiration = models.DateField(null=True,blank=True)
	address = models.CharField(max_length=255,null=True,blank=True)
	city = models.CharField(max_length=255,null=True,blank=True)
	state = models.CharField(max_length=50,null=True,blank=True)
	zip = models.CharField(max_length=10,null=True,blank=True)
	country = models.CharField(max_length=5,null=True,blank=True)
	ppid = models.CharField(max_length=255,null=True,blank=True)
	ppvalid = models.DateField(null=True,blank=True)
	
	# store credit card information
	def store_cc(self, cc_number, cvv):
		credit_card = paypalrestsdk.CreditCard({
		# ###CreditCard
		   # A resource representing a credit card that can be
		   # used to fund a payment.
		   "type": get_cc_type(cc_number),
		   "number": cc_number,
		   "expire_month": self.cc_expiration.month,
		   "expire_year": self.cc_expiration.year,
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
			self.ppvalid = datetime.datetime.strptime(credit_card.valid_until[:10], "%Y-%m-%d")
			
			self.save();
			return True
		else:
			print("Error while creating CreditCard:")
			
		return False
	
	
	def charge_cc(self):
		payment = paypalrestsdk.Payment({
				"intent": "sale",
			  	"payer": {
				"payment_method": "credit_card",
			    "funding_instruments": [{
			      	"credit_card_token": {
			        	"credit_card_id": self.ppid }}]},
			
			  "transactions": [{
			    	"amount": {
			      		"total": self.type.monthly_cost,
			      		"currency": "USD" },
		      		"description": "Recurring monthly subscription from repunch.com." 
			  		}]
				})
		
		if payment.create():
			
			invoice = Invoice()
			invoice.account = Account.objects.filter(subscription=self).get()
			
			invoice.charge_date = datetime.datetime.now()
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
		
		
class Invoice(models.Model):
	account = models.ForeignKey(Account)
	charge_date = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=20,null=True,blank=True)
	response_code = models.CharField(max_length=255,null=True,blank=True)
	respose_subcod = models.CharField(max_length=255,null=True,blank=True)
	reason_code = models.CharField(max_length=255,null=True,blank=True)
	auth_code = models.CharField(max_length=255,null=True,blank=True)
	avs_response = models.CharField(max_length=255,null=True,blank=True)
	trans_id = models.CharField(max_length=255,null=True,blank=True)
	amount = models.FloatField(null=True,blank=True)
	
class AssociatedAccountNonce(models.Model):
	""" Used for both Employee and Store registration (warning) """
	account_id = models.CharField(max_length=30)
	verified = models.BooleanField(default=False)
	
class RecaptchaToken(models.Model):
	username = models.CharField(max_length=70)
	attempts = models.IntegerField(default=1)
