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
from parse.notifications import send_email_receipt_monthly_batch,\
send_email_receipt_monthly_failed
from repunch.settings import COMET_RECEIVE_KEY_NAME,\
COMET_RECEIVE_KEY

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        get all of the subscriptions whose stores are active & who
        have been last billed 30+ days ago.
        IMPORTANT! This includes accounts of type FREE, which are
        not charged or included in the email notifications
        """
        # for logging when ran by CRON
        print "Running monthly_billing: " + str(timezone.now())
        
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
                update_store = False
                sub_cost = sub_type[subscription.get(\
                            "subscriptionType")]["monthly_cost"]
                store = None # prevent UnboundLocalError
                if sub_cost == 0: # FREE account
                    subscription.date_last_billed =\
                        subscription.date_last_billed +\
                        relativedelta(days=30)
                    subscription.update()
                else: # PAID account
                    account = Account.objects().get(Store=\
                                subscription.get("Store"),
                                include="Store")
                    store = account.get("store")
                    invoice = subscription.charge_cc(\
                            sub_cost, "Repunch Inc. Recurring " +\
                            "monthly subscription charge", MONTHLY)
                    send_user_email = True
                    if invoice:
                        subscription.date_last_billed =\
                            subscription.date_last_billed +\
                            relativedelta(days=30)
                        subscription.date_charge_failed = None
                        subscription.update()
                    else:
                        subscription.date_charge_failed = date_now
                        # force entering new credit card!
                        subscription.cc_number = None
                        subscription.date_cc_expiration = None
                        subscription.update()
                    
                        # notify user via email- payment is done via 
                        # dashboard to also validate cc realtime
                        # 1st day time range
                        day1_end = date_30_ago.replace()
                        day1_start = day1_end + relativedelta(hours=-24)
                        # 4th day time range
                        day4_end = date_30_ago + relativedelta(days=-4)
                        day4_start = day4_end + relativedelta(hours=-24)
                        # 8th day time range
                        day8_end = date_30_ago + relativedelta(days=-8)
                        day8_start = day8_end + relativedelta(hours=-24)
                        # 14th day time range
                        day14_end = date_30_ago + relativedelta(days=-14)
                        day14_start = day14_end + relativedelta(hours=-24)
                        # only send email after 1, 4, and 8 days
                        last_billed = subscription.date_last_billed
                        if (last_billed >= day1_start and\
                            last_billed <= day1_end) or\
                            (last_billed >= day4_start and\
                            last_billed <= day4_end) or\
                            (last_billed >= day8_start and\
                            last_billed <= day8_end):
                            send_email_receipt_monthly_failed(account, store,
                                subscription)
                                
                        else: # make sure that the store is deactivated 
                            store.active = False
                            store.update()
                            update_store = True
                            if last_billed >= day14_start and\
                                last_billed <= day14_end:
                                # send final notification
                                send_email_receipt_monthly_failed(account,
                                    store, subscription, account_disabled=True)
                            else:
                                send_user_email = False
                        
                    # do not send email after account deactivation
                    if send_user_email:
                        asiss.append((account, store, invoice,
                            subscription))
                        
                # update the logged in users' subscription and store
                payload = {
                    COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                    "updatedSubscription":subscription.jsonify()
                }
                if store and update_store:
                    payload.update({"updatedStore":store.jsonify()})
                comet_receive(subscription.Store, payload)
                        
            # end of while loop
            sub_count -= LIMIT
            skip += LIMIT
            
        # everything is done - send the emails
        send_email_receipt_monthly_batch(asiss)
        
        
        
