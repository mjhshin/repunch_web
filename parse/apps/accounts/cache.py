"""
Some Parse objects that should be available throughout the app lifetime.
"""

from json import dumps

from parse.utils import parse
from parse.apps.accounts.models import SubscriptionType

# make sure that a subscription type of free exist in the DB
free_type = {"name":"Free", "description":"Free membership", 
                "monthly_cost":0, "max_users":1,
                "max_messages":1, "level":0, 
                "status":SubscriptionType.ACTIVE }
free = parse("GET", "classes/SubscriptionType", query={
                "where":dumps(free_type)})
if not 'results' in free or not free['results']:
    free = SubscriptionType(parse("POST", "classes/SubscriptionType", data=free_type))
else:
    free = SubscriptionType(free['results'][0])
