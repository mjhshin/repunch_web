"""
Makes sure that constant data are initialized on Parse.
"""

from json import dumps

from parse.utils import parse

# Value must be the same as parse.apps.accounts.models constants
# cannot import it here since it will cause cyclic imports
ACTIVE = 'Active'
UNLIMITED = -1

# FREE
free_type = {"name":"FREE",
                "monthly_cost":0, "max_users":50,
                "max_messages":1, "level":0, 
                "status": ACTIVE }
free = parse("GET", "classes/SubscriptionType", query={
                "where":dumps(free_type)})
if not 'results' in free or not free['results']:
    free = parse("POST", "classes/SubscriptionType", data=free_type)
else:
    free = free["results"][0]

# MIDDLE
middle_type = {"name":"MIDDLEWEIGHT", 
                "monthly_cost":39, "max_users":150,
                "max_messages":4, "level":1, 
                "status": ACTIVE }
middle = parse("GET", "classes/SubscriptionType", query={
                "where":dumps(middle_type)})
if not 'results' in middle or not middle['results']:
    middle = parse("POST", "classes/SubscriptionType",
                                            data=middle_type)
else:
    middle = middle["results"][0]

# HEAVY
heavy_type = {"name":"HEAVYWEIGHT", 
                "monthly_cost":59, "max_users":UNLIMITED,
                "max_messages":8, "level":2, 
                "status": ACTIVE }
heavy = parse("GET", "classes/SubscriptionType", query={
                "where":dumps(heavy_type)})
if not 'results' in heavy or not heavy['results']:
    heavy = parse("POST", "classes/SubscriptionType",
                                            data=heavy_type)
else:
    heavy = heavy["results"][0]




