"""
Management command for monthly billing.
Must be run nightly!
"""

from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from parse.core.advanced_queries import pointer_query
from parse.apps.stores import MONTHLY

## first get the number of stores to be billed tonight

# get all of the subscriptions whose stores are active and whose
# subscriptionType is not free (0>x) and have been last billed
# 30 days ago.
date_30_ago = timezone.now() + relativedelta(days=-30)



## charge each store!
## if the count if over 1000 then retrive them in chunks
