from django.core.mail import send_mail

from repunch.settings import PHONE_COST_UNIT_COST, EMAIL_HOST_USER,\
ORDER_PLACED_EMAILS

# Value must be the same as parse.apps.accounts.models constants
# cannot import it here since it will cause cyclic imports
ACTIVE = 'Active'
INACTIVE = 'Inactive'

FREE = "FREE"
MIDDLEWEIGHT = "MIDDLEWEIGHT"
HEAVYWEIGHT = "HEAVYWEIGHT"

UNLIMITED = -1
ERROR = "Billing Error"

# FREE
free_type = {"name":FREE,
                "monthly_cost":0, "max_users":50,
                "max_messages":1, "level":0, 
                "status": ACTIVE }

# MIDDLE
middle_type = {"name":MIDDLEWEIGHT, 
                "monthly_cost":39, "max_users":150,
                "max_messages":4, "level":1, 
                "status": ACTIVE }

# HEAVY
heavy_type = {"name":HEAVYWEIGHT, 
                "monthly_cost":59, "max_users":UNLIMITED,
                "max_messages":8, "level":2, 
                "status": ACTIVE }

sub_type = {
    0:free_type,
    1:middle_type,
    2:heavy_type,
}

def order_placed(amount, store):
    """
    Handle event where an order for phones are placed by a store
    at signup or update account.
    """
    store.get('subscription').charge_cc(\
        PHONE_COST_UNIT_COST*amount,
        "Repunch Inc. Order placed on " +\
        str(amount) + " phones")
    rtlr = 'ORDER PLACED by ' +  store.store_name
    msg = "Business name: " + store.get('store_name') + "\n" +\
        "Owner name: " + store.get('first_name') + " " +\
        store.get('last_name') + "\n" +\
        "Store ID: " + store.objectId + "\n" +\
        "Phone number: " + store.get('phone_number') + "\n" +\
        "Subscription Type: " + sub_type[store.get("subscription").get('subscriptionType')]['name'] + "\n" +\
        "Subscription Status: " + store.get('subscription').get('status') + "\n" +\
        "Amount Ordered: " + str(amount) + "\n" +\
        "Total charged: "  + str(PHONE_COST_UNIT_COST*amount) + "\n"
        
    send_mail(rtlr, msg, EMAIL_HOST_USER, 
        ORDER_PLACED_EMAILS, fail_silently=True)

