"""
Management command for monthly billing.
Must be run nightly!
"""

from django.utils import timezone
from django.core.management.base import BaseCommand

from libs.dateutil.relativedelta import relativedelta
from parse.core.advanced_queries import pointer_query
from parse.comet import comet_receive
from parse.apps.stores import MONTHLY
from parse.apps.stores.models import Subscription
from parse.apps.accounts.models import Account
from parse.apps.accounts import sub_type
from parse.notifications import send_email_receipt_monthly
from repunch.settings import COMET_RECEIVE_KEY_NAME,\
COMET_RECEIVE_KEY

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        get all of the subscriptions whose stores are active & who
        have been last billed 30 days ago.
        IMPORTANT! This includes accounts of type FREE, which are
        not charged or included in the email notifications- simply
        set the date last billed to now.
        """
        date_30_ago = timezone.now() + relativedelta(days=-30)
        date_now = timezone.now()
        sub_count = pointer_query("Subscription",
            {"date_last_billed__lte":date_30_ago},
                "Store", "Store", {"active":True}, count=True)
                
        asiss = []
        # get 500 subscriptions at a time
        LIMIT, skip = 500, 0
        while sub_count > 0:
            for each in pointer_query("Subscription",
                {"date_last_billed__lte":date_30_ago}, "Store",
                    "Store", {"active":True}, limit=LIMIT,
                    skip=skip, order="createdAt")['results']:
                subscription = Subscription(**each)
                sub_cost = sub_type[subscription.get(\
                            "subscriptionType")]["monthly_cost"]
                if sub_cost == 0: # FREE account
                    subscription.date_last_billed =\
                        subscription.date_last_billed +\
                        relativedelta(days=30)
                    subscription.update()
                else:
                    account = Account.objects().get(Store=\
                                subscription.get("Store"))
                    store = account.get("store")
                    invoice = subscription.charge_cc(\
                            sub_cost, "description", MONTHLY)
                    if invoice:
                        subscription.date_last_billed =\
                            subscription.date_last_billed +\
                            relativedelta(days=30)
                        subscription.update()
                    else:
                        # send the user an email TODO
                        # payment is done via the dashboard so that 
                        # the credit card may also be validated
                        
                    asiss.append((account, store, invoice,
                        subscription))
                        
                # update the logged in users' subscriptions
                payload = {
                    COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                    "updatedSubscription":subscription.jsonify()
                }
                comet_receive(subscription.Store, payload)
                        
            # end of while loop
            sub_count -= LIMIT
            skip += LIMIT
            
        # everything is done - send the emails
        send_email_receipt_monthly(asiss)
        
        
        
