"""
Management command for monthly billing.
Must be run nightly!
"""

from libs.dateutil.relativedelta import relativedelta

from parse.core.advanced_queries import relational_query
from parse.apps.stores import MONTHLY

## first get the number of stores to be billed tonight

# get all of the stores that are active
# count = relational_query



## charge each store!
## if the count if over 1000 then retrive them in chunks
