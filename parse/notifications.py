"""
Emails notifications
"""

from importlib import import_module

from django.core import mail
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from django.template import Template, Context

from repunch.settings import ABSOLUTE_HOST, FS_SITE_DIR,\
EMAIL_HOST_USER, STATIC_URL, ABSOLUTE_HOST_ALIAS, DEBUG,\
ORDER_PLACED_EMAILS

def get_notification_ctx():
    """
    Cannot declare as a constant. The reverse method crashes the app.
    """
    return {
        'ABSOLUTE_HOST_ALIAS':ABSOLUTE_HOST_ALIAS,
        'ABSOLUTE_HOST':ABSOLUTE_HOST,
        'ICON_URL':STATIC_URL + "manage/images/email_icon.png", 
        'STORE_INDEX':reverse('store_index'),
        'EMAIL_HOST_USER': EMAIL_HOST_USER,
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

def send_email_receipt(account, invoice, amount, connection=None):
    """
    Sends the user a pretty receipt.
    """
    with open(FS_SITE_DIR +\
        "/templates/manage/notification-receipt.html", 'r') as f:
        template = Template(f.read())
   
    store = account.get("store")
    # for account
    subject = "Repunch Inc. transaction receipt."
    ctx = get_notification_ctx()
    ctx.update({
            'store': store,
            'amount': amount,
            'invoice': invoice,
            'for_customer': True})
    body = template.render(Context(ctx)).__str__()
            
    emails = []
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=[account.get('email')])
    email.attach_alternative(body, 'text/html')
    emails.append(email)
    
    # for admins
    subject = "Smartphone(s) purchased by " +\
         store.get_owner_fullname() + "."
    ctx = get_notification_ctx()
    ctx.update({
            'account': account,
            'store': store,
            'amount': amount,
            'invoice': invoice,
            'for_customer': False})
    body = template.render(Context(ctx)).__str__()
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=ORDER_PLACED_EMAILS)
    email.attach_alternative(body, 'text/html')
    emails.append(email)
    
    _send_emails(emails, connection)

def send_email_signup(account, connection=None):
    """
    Sends a welcome notification to the account and admins.
    """
    # for new account
    with open(FS_SITE_DIR +\
        "/templates/manage/notification.html", 'r') as f:
        template = Template(f.read())
        
    store = account.get("store")
    subject = "Welcome to Repunch " + store.get_owner_fullname() + "."
    ctx = get_notification_ctx()
    ctx.update({'store':store})
    body = template.render(Context(ctx)).__str__()
    emails = []
    
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=[account.get('email')])
    email.attach_alternative(body, 'text/html')
    emails.append(email)
    
    # for admins
    with open(FS_SITE_DIR +\
        "/templates/manage/notification-newuser.html", 'r') as f:
        template = Template(f.read())
    
    subject = "New business: "+account.get("store").get("store_name")
    AccountActivate = getattr(import_module('apps.accounts.models'),
                                "AccountActivate")
    ctx = get_notification_ctx()
    ctx.update({
        'account': account,
        'store': account.get("store"),
        'activate': AccountActivate.objects.create(\
        				store_id=store.objectId),
    })
    body = template.render(Context(ctx)).__str__()
    
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=ORDER_PLACED_EMAILS)
    email.attach_alternative(body, 'text/html')
    emails.append(email)
    
    _send_emails(emails, connection)
   
