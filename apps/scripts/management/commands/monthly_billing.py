"""
Management command for monthly billing.
Must be run nightly!
"""

from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from parse.core.advanced_queries import pointer_query
from parse.apps.stores import MONTHLY
from parse.apps.stores.models import Subscription

## first get the number of stores to be billed tonight

# get all of the subscriptions whose stores are active and whose
# subscriptionType is not free (0>x) and have been last billed
# 30 days ago.
date_30_ago = timezone.now() + relativedelta(days=-30)
sub_count = pointer_query("Subscription", {"subscriptionType1":1,
    "subscriptionType2":2, "date_last_billed__lte":date_30_ago},
    "Store", "Store", {"active":True, limit}, count=True)
    
if sub_count == 0:
    return
    
subscriptions = []
if sub_count < 900:
    res = pointer_query("Subscription", {"subscriptionType1":1,
        "subscriptionType2":2, "date_last_billed__lte":date_30_ago},
        "Store", "Store", {"active":True, limit})['results']
    for each in res:
        
else:
    


# if the count if over 900 then retrieve them in chunks
