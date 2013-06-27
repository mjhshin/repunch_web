from django.core import mail

from parse.notifications import send_email_receipt
from repunch.settings import PHONE_COST_UNIT_COST, EMAIL_HOST_USER,\
ORDER_PLACED_EMAILS, DEBUG

FREE = "FREE"
MIDDLEWEIGHT = "MIDDLEWEIGHT"
HEAVYWEIGHT = "HEAVYWEIGHT"

UNLIMITED = -1
ERROR = "Billing Error"

# FREE
free_type = {"name":FREE,
                "monthly_cost":0, "max_users":50,
                "max_messages":1, "level":0}

# MIDDLE
middle_type = {"name":MIDDLEWEIGHT, 
                "monthly_cost":39, "max_users":150,
                "max_messages":4, "level":1}

# HEAVY
heavy_type = {"name":HEAVYWEIGHT, 
                "monthly_cost":59, "max_users":UNLIMITED,
                "max_messages":8, "level":2}

sub_type = {
    0:free_type,
    1:middle_type,
    2:heavy_type,
}

def _send_emails(emails, connection=None):
    """
    Proceed to send the emails.
    """
    # prep and send the email
    if connection:
        conn = connection
    else:
        conn = mail.get_connection(fail_silently=(not DEBUG))
        conn.open()
        
    conn.send_messages(emails)
    
    if not connection:
        conn.close()

def user_signup(account, connection=None):
    """
    Send an email to ORDER_PLACED_EMAILS about the new user.
    """
    store = account.get('store')
    subject = 'NEW USER: ' +  store.get('store_name')
    msg = "Business name: " + store.get('store_name') + "\n" +\
        "Owner name: " + store.get('first_name') + " " +\
        store.get('last_name') + "\n" +\
        "Store ID: " + store.objectId + "\n" +\
        "Username: " + account.get('username') + "\n" +\
        "Email: " + account.get('email') + "\n" +\
        "Phone number: " + store.get('phone_number') + "\n" +\
        "Subscription Type: " + sub_type[store.get("subscription").get('subscriptionType')]['name'] + "\n" +\
        "Account is Active: " + str(store.get('active')) + "\n"
        
    m = mail.EmailMessage(subject, msg, EMAIL_HOST_USER,
                ORDER_PLACED_EMAILS)
    _send_emails([m], connection)

def order_placed(amount, store, account, connection=None):
    """
    Handle event where an order for phones are placed by a store
    at signup or update account.
    
    TODO replace with pretty template =)
    """
    invoice = store.get('subscription').charge_cc(\
        PHONE_COST_UNIT_COST*amount,
        "Repunch Inc. Order placed on " +\
        str(amount) + " phones", "smartphone")
        
    subject = 'ORDER PLACED by ' +  store.get('store_name')
    msg = "Business name: " + store.get('store_name') + "\n" +\
        "Owner name: " + store.get('first_name') + " " +\
        store.get('last_name') + "\n" +\
        "Store ID: " + store.objectId + "\n" +\
        "Username: " + account.get('username') + "\n" +\
        "Email: " + account.get('email') + "\n" +\
        "Phone number: " + store.get('phone_number') + "\n" +\
        "Subscription Type: " + sub_type[store.get("subscription").get('subscriptionType')]['name'] + "\n" +\
        "Account is Active: " + str(store.get('active')) + "\n" +\
        "Amount Ordered: " + str(amount) + "\n" +\
        "Total charged (USD): $"  + str(PHONE_COST_UNIT_COST*int(amount)) + "\n" +\
        "\nPAYPAL INFO: \n" + invoice.to_message_plain()
        
    # send receipt to recipient
    send_email_receipt(account, invoice, amount, connection)
    # send to us
    m = mail.EmailMessage(subject, msg, EMAIL_HOST_USER,
            ORDER_PLACED_EMAILS)
    _send_emails([m], connection)

