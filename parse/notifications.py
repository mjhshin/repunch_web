"""
Emails notifications
"""

from importlib import import_module
import pytz

from django.core import mail
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.html import strip_tags
# need to import loader though not used since the loader is not
# implicitly imported when running as a management command.
from django.template import Template, Context, loader

from libs.dateutil.relativedelta import relativedelta
from parse.apps.accounts import sub_type
from repunch.settings import ABSOLUTE_HOST, FS_SITE_DIR,\
EMAIL_HOST_USER, STATIC_URL, ABSOLUTE_HOST_ALIAS, DEBUG,\
ORDER_PLACED_EMAILS, TIME_ZONE, ADMINS, MAIN_TRANSPORT_PROTOCOL

EMAIL_SIGNUP_SUBJECT_PREFIX = "New business: "

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
        'MAIN_TRANSPORT_PROTOCOL': MAIN_TRANSPORT_PROTOCOL,
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
        
def send_email_receipt_monthly(asiss, connection=None):
    """
    Sends users a receipt and sends ORDER_PLACED_EMAILS
    an email containing a list 
    of stores that have been charged their monthly bill.
    
    asiss (account store invoice subscription) 
    is a list in the following format:
    [
        (account1, store1, invoice1, subscription1),
        (account2, store2, invoice2, subscription2),
        ...
    ]
    """
    with open(FS_SITE_DIR +\
        "/templates/manage/notification-receipt-monthly.html", 'r') as f:
        template = Template(f.read())
    emails = []
    date_30_ago = timezone.now() + relativedelta(days=-30)
    date_now = timezone.now()
    # for accounts
    for asis in asiss:
        subscription = asis[3]
        if not subscription: 
            continue
        account = asis[0]
        store = asis[1]
        invoice = asis[2]
        subject = "Repunch Inc. monthly service charge."
        ctx = get_notification_ctx()
        ctx.update({'store': store, 'invoice': invoice,
            "date_30_ago":date_30_ago, "date_now":date_now,
            "sub_type":sub_type, "subscription":subscription})
        body = template.render(Context(ctx)).__str__()
                
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), to=[account.get('email')])
        email.attach_alternative(body, 'text/html')
        emails.append(email)
    # for ORDER_PLACED_EMAILS
    with open(FS_SITE_DIR +\
        "/templates/manage/notification-receipt-monthly-admin.html", 'r') as f:
        template = Template(f.read())
    date = timezone.localtime(timezone.now(),pytz.timezone(TIME_ZONE))
    subject = "Monthly billing results : " + date.strftime("%b %d %Y")
    ctx = get_notification_ctx()
    ctx.update({'asiss': asiss, "date":date, "sub_type":sub_type})
    body = template.render(Context(ctx)).__str__()
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=ORDER_PLACED_EMAILS)
    email.attach_alternative(body, 'text/html')
    emails.append(email)
    
    _send_emails(emails, connection)

def send_email_receipt_smartphone(account, subscription, invoice,
    amount, connection=None):
    """
    Sends the user and ORDER_PLACED_EMAILS pretty receipt.
    """
    with open(FS_SITE_DIR +\
        "/templates/manage/notification-receipt-smartphone.html", 'r') as f:
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
    
    # for ORDER_PLACED_EMAILS
    subject = "Smartphone(s) purchased by " +\
         store.get_owner_fullname() + "."
    ctx = get_notification_ctx()
    ctx.update({
            'account': account,
            'subscription': subscription,
            'store': store,
            'amount': amount,
            'invoice': invoice,
            'sub_type': sub_type,
            'for_customer': False})
    body = template.render(Context(ctx)).__str__()
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=ORDER_PLACED_EMAILS)
    email.attach_alternative(body, 'text/html')
    emails.append(email)
    
    _send_emails(emails, connection)
    

def send_email_signup(account, connection=None):
    """
    Sends a welcome notification to the account and 
    ORDER_PLACED_EMAILS.
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
    
    # for ORDER_PLACED_EMAILS
    with open(FS_SITE_DIR +\
        "/templates/manage/notification-newuser.html", 'r') as f:
        template = Template(f.read())
    
    subject = EMAIL_SIGNUP_SUBJECT_PREFIX +\
        account.get("store").get("store_name")
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
    
    
def send_email_suspicious_activity(account, store, chunk1, chunk2,\
        start, end, connection=None):
    """
    chunk1 and chunk2 are a list of dictionaries - 
    See the detect_suspicious_activity management command docstring.
    Note that start and end are utc dates.
    """
    # need to activate the store's timezone for template rendering!
    timezone.activate(pytz.timezone(store.store_timezone))
    
    with open(FS_SITE_DIR +\
        "/templates/manage/notification-suspicious-activity.html",
            'r') as f:
        template = Template(f.read())
        
    subject = "Repunch Inc. Suspicious activity has been detected " +\
                "at " + store.store_name + "."
    ctx = get_notification_ctx()
    ctx.update({'store':store, 'start':start, 'end':end, 
                'chunks':(chunk1, chunk2)})
    body = template.render(Context(ctx)).__str__()
    
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=[account.get('email')])
    email.attach_alternative(body, 'text/html')
    
    _send_emails([email], connection)
    
    
def send_email_passed_user_limit(account, store, package,
        connection=None):
    """
    Used by management command passed_user_limit.
    """
    # need to activate the store's timezone for template rendering!
    timezone.activate(pytz.timezone(store.store_timezone))
    
    with open(FS_SITE_DIR +\
        "/templates/manage/notification-passed-user-limit.html",
            'r') as f:
        template = Template(f.read())
        
    subject = "Repunch Inc. Alert. Your store, " +\
        store.get("store_name") + " has passed the user limit."
    ctx = get_notification_ctx()
    ctx.update({'store':store, 'package':package})
    body = template.render(Context(ctx)).__str__()
    
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=[account.get('email')])
    email.attach_alternative(body, 'text/html')
    
    _send_emails([email], connection)
    
   
def send_email_account_upgrade(account, store, package,
        connection=None):
    """
    User for notifying users that their account has been upgraded.
    """
    # need to activate the store's timezone for template rendering!
    timezone.activate(pytz.timezone(store.store_timezone))
    
    with open(FS_SITE_DIR +\
        "/templates/manage/notification-account-upgraded.html",
            'r') as f:
        template = Template(f.read())
        
    subject = "Repunch Inc. Your account has been upgraded."
    ctx = get_notification_ctx()
    ctx.update({'store':store, 'package':package})
    body = template.render(Context(ctx)).__str__()
    
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=[account.get('email')])
    email.attach_alternative(body, 'text/html')
    
    _send_emails([email], connection)
   

def send_email_selenium_test_results(tests, connection=None):
    """
    Used by selenium tests to send the results of the test to ADMINS.
    tests has the following format:
        tests = [
            {'section_name": section1,
                'parts': [ {'success':True, 'test_name':test1}, ... ],
            ...
        ]
    """
    with open(FS_SITE_DIR +\
        "/templates/manage/notification-selenium-test-results.html",
            'r') as f:
        template = Template(f.read())
        
    date = timezone.localtime(timezone.now(),pytz.timezone(TIME_ZONE))
    subject = "Repunch Inc. Selenium test results."
    ctx = get_notification_ctx()
    ctx.update({'date':date, 'tests':tests})
    body = template.render(Context(ctx)).__str__()
    
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=(ADMINS[0][1], ))
    email.attach_alternative(body, 'text/html')
    
    _send_emails([email], connection)
   
    
    
    
    
    
    
    
    
   
