"""
Some Parse objects that should be available throughout the app lifetime.
"""

from json import dumps
from parse.utils import parse

# make sure that a subscription type of free exist in the DB
free_type = {"name":"Free", "monthly_cost":0, "status":1}
free = parse("GET", "classes/SubscriptionType", query={
                "where":dumps(free_type)})
if not free:
    free = parse("POST", "classes/SubscriptionType", data=free_type)

