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
        # get all of the subscriptions whose stores are active & whose
        # subscriptionType is not free (0>x) and have been last billed
        # 30 days ago.
        date_30_ago = timezone.now() + relativedelta(days=-30)
        date_now = timezone.now()
        sub_count = pointer_query("Subscription",
            {"subscriptionType1":1, "subscriptionType2":2,
                "date_last_billed__lte":date_30_ago},
                "Store", "Store", {"active":True}, count=True)
                
        asiss = []
        if sub_count < 900:
            res = pointer_query("Subscription",
                {"subscriptionType1":1, "subscriptionType2":2,
                    "date_last_billed__lte":date_30_ago},
                    "Store", "Store", {"active":True})['results']
            for each in res:
                subscription = Subscription(**each)
                account = Account.objects().get(Store=\
                            subscription.get("Store"))
                store = account.get("store")
                invoice = subscription.charge_cc(\
                        sub_type[subscription.get(\
                        "subscriptionType")]["monthly_cost"],
                        "description", MONTHLY)
                if invoice:
                    subscription.date_last_billed = date_now
                    subscription.update()
                asiss.append((account, store, invoice, subscription))
        else: 
            pass 
        # if the count is over 900 then retrieve them in chunks TODO
        # 900 signed up in the same day? unlikely but will handle it.
            

        send_email_receipt_monthly(asiss)
