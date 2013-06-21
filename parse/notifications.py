"""
Emails notifications
"""

from django.core import mail
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from django.template import Template, Context

from repunch.settings import ABSOLUTE_HOST, FS_SITE_DIR,\
EMAIL_HOST_USER, STATIC_URL, ABSOLUTE_HOST_ALIAS, DEBUG

def send_email_receipt(account, data):
    """
    Sends the user a pretty receipt.
    """
    pass

def send_email_signup(account, connection=None):
    """
    Sends a welcome notification to the account.
    """
    with open(FS_SITE_DIR +\
        "/templates/manage/notification.html", 'r') as f:
        template = Template(f.read())
        
    entity = account.get(account.get('account_type'))
    subject = "Welcome to Repunch " + entity.first_name.capitalize()+\
                " " + entity.last_name.capitalize() + "."
    body = template.render(Context({
            'ABSOLUTE_HOST_ALIAS':ABSOLUTE_HOST_ALIAS,
            'ABSOLUTE_HOST':ABSOLUTE_HOST,
            'ICON_URL':STATIC_URL + "manage/images/email_icon.png", 
            'STORE_INDEX':reverse('store_index'),
            'EMAIL_HOST_USER': EMAIL_HOST_USER,
            'entity':entity,
            })).__str__()
            
    emails = []
    email = mail.EmailMultiAlternatives(subject,
                strip_tags(body), to=[account.get('email')])
    email.attach_alternative(body, 'text/html')
    emails.append(email)
        
    # prep and send the email
    if connection:
        conn = connection
    else:
        conn = mail.get_connection(fail_silently=(not DEBUG))
        conn.open()
        
    conn.send_messages(emails)
    
    if not connection:
        conn.close()
