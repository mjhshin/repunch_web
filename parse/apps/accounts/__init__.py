"""
Makes sure that constant data are initialized on Parse.
"""

from json import dumps

from parse.utils import parse

# Value must be the same as parse.apps.accounts.SubscriptionType.ACTIVE
# cannot import it here since it will cause cyclic imports
ACTIVE = 'Active'

# make sure that a subscription type of free exist in the DB
free_type = {"name":"Free", "description":"Free membership", 
                "monthly_cost":0, "max_users":50,
                "max_messages":1, "level":0, 
                "status": ACTIVE }
free = parse("GET", "classes/SubscriptionType", query={
                "where":dumps(free_type)})
if not 'results' in free or not free['results']:
    free = parse("POST", "classes/SubscriptionType", data=free_type)
else:
    free = free["results"][0]

# TODO MIDDLE AND HEAVY
