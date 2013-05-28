from parse.utils import parse

# make sure that a subscription type of free exist in the DB
def get_free_subscriptiontype():
    free_type = {"name":"Free", "monthly_cost":0, "status":1}
    free = parse("GET", "classes/SubscriptionType", query=free_type)
    if not free or len(free["results"]) == 0:
        free = parse("POST", "classes/SubscriptionType", data=free_type)
    


