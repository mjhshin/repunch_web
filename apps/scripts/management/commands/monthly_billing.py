"""
Management command for monthly billing.
Must be run nightly!
"""

from django.utils import timezone
from django.core.management.base import BaseCommand

from libs.dateutil.relativedelta import relativedelta
from parse.core.advanced_queries import pointer_query
from parse.apps.stores import MONTHLY
from parse.apps.stores.models import Subscription
from parse.apps.accounts.models import Account
from parse.apps.accounts import sub_type
from parse.notifications import send_email_receipt_monthly

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
                    subscription.date_last_billed = date_now
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
                            relativedelta(days=-30)
                        subscription.update()
                        # if the charge failed before
                        if subscription.date_charge_failed:
                            subscription.date_charge_failed = None
                            subscription.update()
                    else:
                        # set the date_charge_failed if none
                        if not subscription.date_charge_failed:
                            subscription.date_charge_failed =\
                                timezone.now()
                            subscription.update()
                        # send the user an email every day # TODO
                        
                    
                    asiss.append((account, store, invoice,
                        subscription))
                        
                # TODO comet_receive - update the logged in users' subscriptions
                
            # end of while loop
            sub_count -= LIMIT
            skip += LIMIT
            
        # everything is done - send the emails
        send_email_receipt_monthly(asiss)
        
        
        
