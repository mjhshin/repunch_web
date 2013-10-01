"""
Emails notifications.

If a connection is provided, then that connection will be used to
send the email in the same thread.

If a connection is NOT provided, then a connection is created and
the sending occurs in a new thread.
"""

from importlib import import_module
from threading import Thread
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
EMAIL_FROM, STATIC_URL, DEBUG,\
ORDER_PLACED_EMAILS, TIME_ZONE, ADMINS, MAIN_TRANSPORT_PROTOCOL

# declare here for selenium tests use also
EMAIL_SIGNUP_SUBJECT_PREFIX = "New business: "
EMAIL_SIGNUP_WELCOME_SUBJECT_PREFIX = "Welcome to Repunch "
EMAIL_UPGRADE_SUBJECT = "Repunch Inc. Your subscription has been upgraded."
EMAIL_MONTHLY_SUBJECT = "Repunch Inc. monthly service charge."

def get_notification_ctx():
    """
    Cannot declare as a constant. The reverse method crashes the app.
    """
    return {
        'ABSOLUTE_HOST':ABSOLUTE_HOST,
        'ICON_URL':STATIC_URL + "manage/images/email_icon.png", 
        'STORE_INDEX':reverse('store_index'),
        'EMAIL_FROM': EMAIL_FROM,
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
        
def send_email_receipt_monthly_failed(account, store, subscription,
    account_disabled=False, connection=None):
    """
    Called in monthly billing if charging cc failed.
    Sends an email to the account holder.
    """
    def _wrapper():
        # need to activate the store's timezone for template rendering!
        timezone.activate(pytz.timezone(store.store_timezone))
        with open(FS_SITE_DIR +\
            "/templates/manage/notification-receipt-monthly-failed.html", 'r') as f:
            template = Template(f.read())
        # variable names are misleading here ><
        date_now = subscription.date_last_billed +\
            relativedelta(days=30)
        #########
        # the 14 day sequence just like passed user limit
        date_disable = date_now + relativedelta(days=14)
        subject = "Repunch Inc. important service notice."
        ctx = get_notification_ctx()
        ctx.update({'store': store, "date_disable":date_disable,
            "date_now":date_now,
            "account_disabled": account_disabled,
            "sub_type":sub_type, "subscription":subscription})
        body = template.render(Context(ctx)).__str__()
                
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), EMAIL_FROM,
                    [account.get('email')])
        email.attach_alternative(body, 'text/html')
            
        _send_emails([email], connection)
    
    if connection:
        _wrapper()
    else:
        Thread(target=_wrapper).start()
        
def send_email_receipt_monthly_success(account, store, subscription,
    invoice, connection=None):
    """
    Called in monthly billing if charging cc was successful.
    Sends an email to the account holder and ORDER_PLACED_EMAILS
    """
    def _wrapper():
        # need to activate the store's timezone for template rendering!
        timezone.activate(pytz.timezone(store.store_timezone))
        with open(FS_SITE_DIR +\
            "/templates/manage/notification-receipt-monthly.html", 'r') as f:
            template = Template(f.read())
        # assumes that subscription's date_last_billed has been 
        # updated prior to this
        # variable names are misleading here ><
        date_30_ago = subscription.date_last_billed +\
            relativedelta(days=-30)
        date_now = subscription.date_last_billed.replace()
        ##########
        emails = []
        subject = EMAIL_MONTHLY_SUBJECT
        ctx = get_notification_ctx()
        ctx.update({'store': store, 'invoice': invoice,
            "account": account, "subscription":subscription,
            "date_30_ago":date_30_ago, "date_now":date_now,
            "sub_type":sub_type, "subscription":subscription})
        body = template.render(Context(ctx)).__str__()
        timezone.deactivate()
                
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), EMAIL_FROM,
                    [account.get('email')])
        email.attach_alternative(body, 'text/html')
        emails.append(email)
        
        # for ORDER_PLACED_EMAILS
        subject = "Monthly billing payment by " +\
            store.get_owner_fullname() + "."
        timezone.activate(pytz.timezone(TIME_ZONE))
        ctx.update({"for_admin": True})
        body = template.render(Context(ctx)).__str__()
        timezone.deactivate()
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), EMAIL_FROM,
                    ORDER_PLACED_EMAILS)
        email.attach_alternative(body, 'text/html')
        emails.append(email)
        
        _send_emails(emails, connection)
    
    if connection:
        _wrapper()
    else:
        Thread(target=_wrapper).start()
        
def send_email_receipt_monthly_batch(asiss, connection=None):
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
    def _wrapper():
        with open(FS_SITE_DIR +\
            "/templates/manage/notification-receipt-monthly.html", 'r') as f:
            template = Template(f.read())
        emails = []
        # for accounts
        for asis in asiss:
            invoice = asis[2]
            if not invoice: # failed to charge user
                continue
            subscription = asis[3]
            account = asis[0]
            store = asis[1]
            timezone.activate(pytz.timezone(store.store_timezone))
            # assumes that subscription's date_last_billed has been 
            # updated prior to this
            # variable names are misleading here ><
            date_30_ago = subscription.date_last_billed +\
                relativedelta(days=-30)
            date_now = subscription.date_last_billed.replace()
            #############
            subject = EMAIL_MONTHLY_SUBJECT
            ctx = get_notification_ctx()
            ctx.update({'store': store, 'invoice': invoice,
                "date_30_ago":date_30_ago, "date_now":date_now,
                "sub_type":sub_type, "subscription":subscription})
            body = template.render(Context(ctx)).__str__()
            timezone.deactivate()
                    
            email = mail.EmailMultiAlternatives(subject,
                        strip_tags(body), EMAIL_FROM,
                        [account.get('email')])
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
        timezone.activate(pytz.timezone(TIME_ZONE))
        body = template.render(Context(ctx)).__str__()
        timezone.deactivate()
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), EMAIL_FROM,
                    ORDER_PLACED_EMAILS)
        email.attach_alternative(body, 'text/html')
        emails.append(email)
        
        _send_emails(emails, connection)
        
    if connection:
        _wrapper()
    else:
        Thread(target=_wrapper).start()

def send_email_receipt_ipod(account, subscription, invoice,
    amount, connection=None):
    """
    Sends the user and ORDER_PLACED_EMAILS pretty receipt.
    """
    def _wrapper():
        with open(FS_SITE_DIR +\
            "/templates/manage/notification-receipt-ipod.html", 'r') as f:
            template = Template(f.read())
       
        store = account.get("store")
        timezone.activate(pytz.timezone(store.store_timezone))
        # for account
        subject = "Repunch Inc. transaction invoice."
        ctx = get_notification_ctx()
        ctx.update({
                'store': store,
                'amount': amount,
                'invoice': invoice,
                'for_customer': True})
        body = template.render(Context(ctx)).__str__()
        timezone.deactivate()
                
        emails = []
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), EMAIL_FROM,
                    [account.get('email')])
        email.attach_alternative(body, 'text/html')
        emails.append(email)
        
        # for ORDER_PLACED_EMAILS
        subject = "iPod Touch(es) purchased by " +\
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
                
        timezone.activate(pytz.timezone(TIME_ZONE))
        body = template.render(Context(ctx)).__str__()
        timezone.deactivate()
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), EMAIL_FROM,
                    ORDER_PLACED_EMAILS)
        email.attach_alternative(body, 'text/html')
        emails.append(email)
        
        _send_emails(emails, connection)
    
    if connection:
        _wrapper()
    else:
        Thread(target=_wrapper).start()

def send_email_signup(account, connection=None):
    """
    Sends a welcome notification to the account and 
    ORDER_PLACED_EMAILS.
    """
    def _wrapper():
        # for new account
        with open(FS_SITE_DIR +\
            "/templates/manage/notification-newuser.html", 'r') as f:
            template = Template(f.read())
            
        store = account.get("store")
        subject = EMAIL_SIGNUP_WELCOME_SUBJECT_PREFIX +\
            store.get_owner_fullname()
        ctx = get_notification_ctx()
        ctx.update({'store':store})
        body = template.render(Context(ctx)).__str__()
        emails = []
        
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), EMAIL_FROM,
                    [account.get('email')])
        email.attach_alternative(body, 'text/html')
        emails.append(email)
        
        # for ORDER_PLACED_EMAILS
        with open(FS_SITE_DIR +\
            "/templates/manage/notification-newuser-admin.html", 'r') as f:
            template = Template(f.read())
        
        subject = EMAIL_SIGNUP_SUBJECT_PREFIX +\
            account.get("store").get("store_name")
        StoreActivate = getattr(import_module('apps.stores.models'),
                                    "StoreActivate")
        ctx = get_notification_ctx()
        ctx.update({
            'account': account,
            'store': account.get("store"),
            'activate': StoreActivate.objects.create(\
            				store_id=store.objectId),
        })
        timezone.activate(pytz.timezone(TIME_ZONE))
        body = template.render(Context(ctx)).__str__()
        timezone.deactivate()
        
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), EMAIL_FROM,
                    ORDER_PLACED_EMAILS)
        email.attach_alternative(body, 'text/html')
        emails.append(email)
        
        _send_emails(emails, connection)
    
    if connection:
        _wrapper()
    else:
        Thread(target=_wrapper).start()
    
def send_email_suspicious_activity(account, store, chunk1, chunk2,\
        start, end, connection=None):
    """
    chunk1 and chunk2 are a list of dictionaries - 
    See the detect_suspicious_activity management command docstring.
    Note that start and end are utc dates.
    """
    def _wrapper():
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
                    strip_tags(body), EMAIL_FROM,
                    [account.get('email')])
        email.attach_alternative(body, 'text/html')
        
        _send_emails([email], connection)
    
    if connection:
        _wrapper()
    else:
        Thread(target=_wrapper).start()
    
def send_email_passed_user_limit(account, store, package,
        connection=None):
    """
    Used by management command passed_user_limit.
    """
    def _wrapper():
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
                    strip_tags(body), EMAIL_FROM,
                    [account.get('email')])
        email.attach_alternative(body, 'text/html')
        
        _send_emails([email], connection)
    
    if connection:
        _wrapper()
    else:
        Thread(target=_wrapper).start()
   
def send_email_account_upgrade(account, store, package,
        connection=None):
    """
    User for notifying users that their account has been upgraded.
    """
    def _wrapper():
        # need to activate the store's timezone for template rendering!
        timezone.activate(pytz.timezone(store.store_timezone))
        
        with open(FS_SITE_DIR +\
            "/templates/manage/notification-subscription-upgraded.html",
                'r') as f:
            template = Template(f.read())
            
        subject = EMAIL_UPGRADE_SUBJECT
        ctx = get_notification_ctx()
        ctx.update({'store':store, 'package':package})
        body = template.render(Context(ctx)).__str__()
        
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), EMAIL_FROM,
                    [account.get('email')])
        email.attach_alternative(body, 'text/html')
        
        _send_emails([email], connection)
   
    if connection:
        _wrapper()
    else:
        Thread(target=_wrapper).start()

def send_email_selenium_test_results(tests, connection=None):
    """
    Used by selenium tests to send the results of the test to ADMINS.
    tests has the following format:
        tests = [
            {'section_name": section1,
                'parts': [ {'success':True, 'test_name':test1,
                            'test_message':'...'}, ... ],
            ...
        ]
    """
    def _wrapper():
        with open(FS_SITE_DIR +\
            "/templates/manage/notification-selenium-test-results.html",
                'r') as f:
            template = Template(f.read())
            
        date = timezone.localtime(timezone.now(),pytz.timezone(TIME_ZONE))
        subject = "Repunch Inc. Selenium test results."
        ctx = get_notification_ctx()
        ctx.update({'date':date, 'tests':tests})
        timezone.activate(pytz.timezone(TIME_ZONE))
        body = template.render(Context(ctx)).__str__()
        timezone.deactivate()
        
        email = mail.EmailMultiAlternatives(subject,
                    strip_tags(body), EMAIL_FROM,
                    [ADMINS[0][1]])
        email.attach_alternative(body, 'text/html')
        
        _send_emails([email], connection)
   
    if connection:
        _wrapper()
    else:
        Thread(target=_wrapper).start()
    
    
    
    
    
    
    
    
   
