"""
Selenium tests for dashboard 'Messages' tab.
"""

from django.core.urlresolvers import reverse
from django.utils import timezone
from selenium.webdriver.common.keys import Keys
from time import sleep

from libs.dateutil.relativedelta import relativedelta
from libs.imap import Mail
from tests import SeleniumTest
from apps.messages.forms import DATE_PICKER_STRFTIME
from parse.apps.accounts.models import Account
from parse.notifications import EMAIL_UPGRADE_SUBJECT

TEST_USER = {
    "username": "clothing",
    "password": "123456",
}

def test_messages():
    # setup
    account = Account.objects().get(username=TEST_USER['username'],
        include="Store.Subscription")
    store = account.store
    subscription = store.subscription

    # set subscriptionType to free
    subscription.subscriptionType = 0
    subscription.update()

    # clear the sent messages relation
    sent_messages = store.get("sentMessages", keys="")
    if sent_messages:
        store.remove_relation("SentMessages_",
            [m.objectId for m in sent_messages])
    # clear the received messages relation
    received_messages = store.get("receivedMessages", keys="")
    if received_messages:
        store.remove_relation("ReceivedMessages_",
            [m.objectId for m in received_messages])
            
    # we can clear the list locally but just re-pull from parse
    account = Account.objects().get(username=TEST_USER['username'],
        include="Store.Subscription")
    store = account.store
    subscription = store.subscription
    
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        
        # FIRST
        {'test_name': "Send message. Filter all. No offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        # SECOND
        {'test_name': "Send message. Filter all. With offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        # THIRD    
        {'test_name': "Send message. Filter idle. No offer. " +\
            "Message limit passed (free) dialog appears"},
        # LIMIT PASSED
        {'test_name': "Upgrading account from the dialog sends the " +\
            "message and upgrades the account to middle"},
        {'test_name': "Email is sent notifying user the upgrade"},
        #
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        # FOURTH
        {'test_name': "Send message. Filter idle. With offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        # FIFTH
        {'test_name': "Send message. Filter most_loyal. No offer. " +\
            "Message limit passed (middle) dialog appears"},
        # LIMIT PASSED
        {'test_name': "Upgrading account from the dialog sends the" +\
            " message and upgrades the account to heavy"},
        {'test_name': "Email is sent notifying user the upgrade"},
        #
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        # SIXTH
        {'test_name': "Send message. Filter most_loyal. With offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        # SEVENTH
        {'test_name': "Send message. Filter all. With offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        # EIGHTH
        {'test_name': "Send message. Filter all. With offer"},
        {'test_name': "Message is in store's sentMessages relation"},
        {'test_name': "Message is visible in page"},
        {'test_name': "Message can be view by clicking on row"},
        # NINTH
        {'test_name': "Send message. Filter all. No offer. " +\
            "Message limit passed (heavy) dialog appears"},
        # LIMIT PASSED
        {'test_name': "Account can no longer be upgraded." +\
            "Message cannot be sent. Clicking okay redirects "+\
            "user to messages index."},
        #
            
        {'test_name': "Subject is required"},
        {'test_name': "Body is required"},
        {'test_name': "Offer title not required if attach offer off"},
        {'test_name': "Expiration not required if attach offer off"},
        {'test_name': "Offer title is required if attach offer on"},
        {'test_name': "Expiration date required if attach offer on"},
        {'test_name': "Expiration date must be at a later date"},
        {'test_name': "Expiration date must be at most 1 year later"},
        
        {'test_name': "Clicking cancel prompts the user in deletion"},
        {'test_name': "Canceling redirects user back to messages" +\
            "index"},
            
    ]
    section = {
        "section_name": "Messages page working properly?",
        "parts": parts,
    }
    test.results.append(section)
    
    ##########  User needs to be logged in to access page
    test.open(reverse("messages_index")) # ACTION!
    sleep(1)
    parts[0]['success'] = test.is_current_url(reverse(\
        'manage_login') + "?next=" + reverse("messages_index"))
        
    # login
    selectors = (
        ("#id_username", TEST_USER['username']),
        ("#id_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(5) 
    
    def send_message(filter, subject, body,
            attach_offer=False, offer_title=None, exp_date=None,):
        """ Must be called at messages index page """
        test.find("#create_message").click()
        sleep(1)
        # set the filter
        test.find("//select[@id='filter']/option[@value='%s']" %\
            (filter,), type="xpath").click()
        # subject
        test.find("#id_subject").send_keys(subject)
        # body
        test.find("#id_body").send_keys(body)
        # attach_offer
        if attach_offer:
            test.find("#id_attach_offer").click()
            # offer title
            if offer_title:
                test.find("#id_offer_title").send_keys(offer_title)
            # exp_date
            if exp_date:
                test.find("#id_date_offer_expiration").send_keys(exp_date)
            
        # submit
        test.find("#send-now").click()
        sleep(5)
        
    def message_in_relation(message_id, test_number):
        if not message_id:
            return
            
        store.sentMessages = None
        parts[test_number]['success'] = store.get("sentMessages", 
            objectId=message_id, count=1, limit=0) == 1
            
    def message_in_page(message_id, test_number):
        if not message_id:
            return
            
        try:
            rows = test.find("#tab-body-sent div.tr a", multiple=True)
            for row in rows:
                if row.get_attribute("href").split("/")[5] ==\
                    message_id:
                    parts[test_number]['success'] = True
        except Exception as e:
            print e
            parts[test_number]['test_message'] = str(e)
        
    def message_viewable(message_id, test_number):
        if not message_id:
            return
        href = reverse("message_details", args=(message_id,))
        try:
            test.find("#tab-body-sent div.tr a[href='%s']" %\
                (href,)).click()
            sleep(2)
            parts[test_number]['success'] = test.is_current_url(href)
        except Exception as e:
            print e
            parts[test_number]['test_message'] = str(e)
        finally:
            # must go back to messages index for the other tests
            test.open(reverse("messages_index"))
                
    # FIRST
    ##########  Send message. Filter all. No offer. 
    message_id = None
    try:
        send_message("all", "msg #1", "body #1")
        parts[1]['success'] = len(test.find(\
            "div.notification.success", multiple=True)) > 0
        message_id = test.driver.current_url.split("/")[5]
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
    finally: # must go back to messages index
        test.open(reverse("messages_index"))
        
    ##########  Message is in store's sentMessages relation. 
    message_in_relation(message_id, 2)
    ##########  Message is visible in page. 
    message_in_page(message_id, 3)
    ##########  Message can be view by clicking on row. 
    message_viewable(message_id, 4)

    # SECOND
    ##########  Send message. Filter all. With offer. 
    message_id = None
    try:
        exp_date = timezone.now() + relativedelta(days=1)
        send_message("all", "msg #2", "body #2", True, "offer#2",
            exp_date.strftime(DATE_PICKER_STRFTIME))
        parts[5]['success'] = len(test.find(\
            "div.notification.success", multiple=True)) > 0
        message_id = test.driver.current_url.split("/")[5]
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
    finally: # must go back to messages index
        test.open(reverse("messages_index"))
    ##########  Message is in store's sentMessages relation. 
    message_in_relation(message_id, 6)
    ##########  Message is visible in page. 
    message_in_page(message_id, 7)
    ##########  Message can be view by clicking on row. 
    message_viewable(message_id, 8) 
        
    # THIRD
    ##########  Send message. Filter idle. No offer. 
    ###         Message limit passed (free) dialog appears.
    message_id = None
    try:
        send_message("idle", "msg #3", "body #3")
        parts[9]['success'] = test.find("#upgrade") is not None
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
        test.open(reverse("messages_index"))
    # LIMIT PASSED
    ##########  Upgrading account from the dialog sends the 
    ###         message and upgrades the account to middle.
    try:
        test.find("#upgrade").click()
        sleep(2)
        test.find("#id_cc_cvv").send_keys("123")
        test.find("#id_recurring").click()
        test.find("#upgrade-form-submit").click()
        sleep(5)
        message_id = test.driver.current_url.split("/")[5]
        subscription.subscriptionType = None
        parts[10]['success'] = test.is_current_url(\
            reverse("message_details", args=(message_id,))) and\
            subscription.get("subscriptionType") == 1
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
    finally: # must go back to messages index
        test.open(reverse("messages_index"))
        
    # open the mail connection
    mail = Mail()
    ##########  Email is sent notifying user the upgrade.
    try:
        parts[11]['success'] = mail.is_mail_sent(\
            EMAIL_UPGRADE_SUBJECT)
    except Exception as e:
        print e
        parts[11]['test_message'] = str(e)
    ##########  Message is in store's sentMessages relation. 
    message_in_relation(message_id, 12)
    ##########  Message is visible in page. 
    message_in_page(message_id, 13)
    ##########  Message can be view by clicking on row. 
    message_viewable(message_id, 14) 

    # FOURTH
    ##########  Send message. Filter idle. With offer. 
    message_id = None
    try:
        exp_date = timezone.now() + relativedelta(days=1)
        send_message("idle", "msg #4", "body #4", True, "offer#4",
            exp_date.strftime(DATE_PICKER_STRFTIME))
        parts[15]['success'] = len(test.find(\
            "div.notification.success", multiple=True)) > 0
        message_id = test.driver.current_url.split("/")[5]
    except Exception as e:
        print e
        parts[15]['test_message'] = str(e)
    finally: # must go back to messages index
        test.open(reverse("messages_index"))
    ##########  Message is in store's sentMessages relation. 
    message_in_relation(message_id, 16)
    ##########  Message is visible in page. 
    message_in_page(message_id, 17)
    ##########  Message can be view by clicking on row. 
    message_viewable(message_id, 18) 
        
    # FIFTH
    ##########  Send message. Filter most_loyal. No offer. 
    ###         Message limit passed (free) dialog appears.
    message_id = None
    try:
        send_message("most_loyal", "msg #5", "body #5")
        parts[19]['success'] = test.find("#upgrade") is not None
    except Exception as e:
        print e
        parts[19]['test_message'] = str(e)
        test.open(reverse("messages_index"))
    # LIMIT PASSED
    ##########  Upgrading account from the dialog sends the 
    ###         message and upgrades the account to heavy.
    try:
        test.find("#upgrade").click()
        sleep(2)
        test.find("#id_cc_cvv").send_keys("123")
        test.find("#id_recurring").click()
        test.find("#upgrade-form-submit").click()
        sleep(5)
        message_id = test.driver.current_url.split("/")[5]
        subscription.subscriptionType = None
        parts[20]['success'] = test.is_current_url(\
            reverse("message_details", args=(message_id,))) and\
            subscription.get("subscriptionType") == 2
    except Exception as e:
        print e
        parts[20]['test_message'] = str(e)
    finally: # must go back to messages index
        test.open(reverse("messages_index"))
    ##########  Email is sent notifying user the upgrade.
    try:
        parts[21]['success'] = mail.is_mail_sent(\
            EMAIL_UPGRADE_SUBJECT)
    except Exception as e:
        print e
        parts[21]['test_message'] = str(e)
    ##########  Message is in store's sentMessages relation. 
    message_in_relation(message_id, 22)
    ##########  Message is visible in page. 
    message_in_page(message_id, 23)
    ##########  Message can be view by clicking on row. 
    message_viewable(message_id, 24) 

    # SIXTH
    ##########  Send message. Filter most_loyal. With offer. 
    message_id = None
    try:
        exp_date = timezone.now() + relativedelta(days=1)
        send_message("most_loyal", "msg #6", "body #6",
            True, "offer#6", exp_date.strftime(DATE_PICKER_STRFTIME))
        parts[25]['success'] = len(test.find(\
            "div.notification.success", multiple=True)) > 0
        message_id = test.driver.current_url.split("/")[5]
    except Exception as e:
        print e
        parts[25]['test_message'] = str(e)
    finally: # must go back to messages index
        test.open(reverse("messages_index"))
    ##########  Message is in store's sentMessages relation. 
    message_in_relation(message_id, 26)
    ##########  Message is visible in page. 
    message_in_page(message_id, 27)
    ##########  Message can be view by clicking on row. 
    message_viewable(message_id, 28) 

    # SEVENTH
    ##########  Send message. Filter all. With offer. 
    message_id = None
    try:
        exp_date = timezone.now() + relativedelta(days=1)
        send_message("all", "msg #7", "body #7", True, "offer#7",
            exp_date.strftime(DATE_PICKER_STRFTIME))
        parts[29]['success'] = len(test.find(\
            "div.notification.success", multiple=True)) > 0
        message_id = test.driver.current_url.split("/")[5]
    except Exception as e:
        print e
        parts[29]['test_message'] = str(e)
    finally: # must go back to messages index
        test.open(reverse("messages_index"))
    ##########  Message is in store's sentMessages relation. 
    message_in_relation(message_id, 30)
    ##########  Message is visible in page. 
    message_in_page(message_id, 31)
    ##########  Message can be view by clicking on row. 
    message_viewable(message_id, 32) 

    # EIGHTH
    ##########  Send message. Filter all. With offer. 
    message_id = None
    try:
        exp_date = timezone.now() + relativedelta(days=1)
        send_message("all", "msg #8", "body #8", True, "offer#8",
            exp_date.strftime(DATE_PICKER_STRFTIME))
        parts[33]['success'] = len(test.find(\
            "div.notification.success", multiple=True)) > 0
        message_id = test.driver.current_url.split("/")[5]
    except Exception as e:
        print e
        parts[33]['test_message'] = str(e)
    finally: # must go back to messages index
        test.open(reverse("messages_index"))
    ##########  Message is in store's sentMessages relation. 
    message_in_relation(message_id, 34)
    ##########  Message is visible in page. 
    message_in_page(message_id, 35)
    ##########  Message can be view by clicking on row. 
    message_viewable(message_id, 36) 

    # NINTH
    ##########  Send message. Filter all. With offer. 
    ###         Message limit passed (heavy) dialog appears. 
    message_id = None
    try:
        send_message("all", "msg #9", "body #9")
        parts[37]['success'] = test.element_exists("#maxed_out")
    except Exception as e:
        print e
        parts[37]['test_message'] = str(e)
        test.open(reverse("messages_index"))
    # LIMIT PASSED
    ##########  Account can no longer be upgraded. Msg cannot be sent.
    ###         Clicking Okay redirects user to messages index.
    try:
        test.find("#maxed_out").click()
        sleep(1)
        parts[38]['success'] =\
            test.is_current_url(reverse("messages_index"))
    except Exception as e:
        print e
        parts[38]['test_message'] = str(e)
        test.open(reverse("messages_index"))
    # 
    
    # goto edit message page
    test.find("#create_message").click()
    sleep(2)
        
    selectors = (
        ("#id_subject", "   "),
        ("#id_body", "   "),
    )
    test.action_chain(0, selectors, action="send_keys")
    test.find("#send-now").click()
    sleep(1)
    ##########  Subject is required.
    try:
        parts[39]['success'] = test.find("#subject_e ul li").text ==\
            "This field is required."
    except Exception as e:
        print e
        parts[39]['test_message']= str(e)
    ##########  Body is required. 
    try:
        parts[40]['success'] = test.find("#body_e ul li").text ==\
            "This field is required."
    except Exception as e:
        print e
        parts[40]['test_message'] = str(e)
    ##########  Offer title not required if attach offer off. 
    try:
        parts[41]['success'] = not test.element_exists(\
            "#offer_title_e ul li")
    except Exception as e:
        print e
        parts[41]['test_message'] = str(e)
    ##########  Expiration not required if attach offer off. 
    try:
        parts[42]['success'] = not test.element_exists(\
            "#date_offer_expiration_e ul li")
    except Exception as e:
        print e
        parts[42]['test_message'] = str(e)
        
    test.find("#id_attach_offer").click()
    test.find("#send-now").click()
    sleep(1)
    ##########  Offer title is required if attach offer on. 
    try:
        parts[43]['success'] =\
            test.find("#offer_title_e ul li").text ==\
            "Please enter a title."
    except Exception as e:
        print e
        parts[43]['test_message'] = str(e)
    ##########  Expiration date required if attach offer on. 
    try:
        parts[44]['success'] =\
            test.find("#date_offer_expiration_e ul li").text ==\
            "Please enter an expiration date."
    except Exception as e:
        print e
        parts[44]['test_message'] = str(e)
        
    ##########  Expiration date must be at a later date. 
    try:
        # don't click attach offer again!
        # test.find("#id_attach_offer").click()
        exp_date = timezone.now() + relativedelta(days=-1)
        test.find("#id_date_offer_expiration").send_keys(\
            exp_date.strftime(DATE_PICKER_STRFTIME))
        test.find("#send-now").click()
        sleep(1)
        parts[45]['success'] = test.find(\
            "#date_offer_expiration_e ul li").text ==\
            "Please enter an expiration date that is later than today."
    except Exception as e:
        print e
        parts[45]['test_message'] = str(e)
    
    ##########  Expiration date must be at most 1 year later. 
    try:
        # don't click attach offer again!
        # test.find("#id_attach_offer").click()
        exp_date = timezone.now() + relativedelta(days=367)
        date_offer = test.find("#id_date_offer_expiration")
        date_offer.clear()
        date_offer.send_keys(\
            exp_date.strftime(DATE_PICKER_STRFTIME))
        test.find("#send-now").click()
        sleep(2)
        parts[46]['success'] = test.find(\
            "#date_offer_expiration_e ul li").text ==\
            "Please enter an expiration date that is less than a year."
    except Exception as e:
        print e
        parts[46]['test_message'] = str(e)

    ##########  Clicking cancel prompts the user in deletion. 
    try:
        test.find("#delete-button").click()
        sleep(1)
        alert = test.switch_to_alert()
        parts[47]['success'] = alert.text is not None
    except Exception as e:
        print e
        parts[47]['test_message'] = str(e)
    ##########  Canceling redirects user back to messages index. 
    try:
        alert.accept()
        sleep(1)
        parts[48]['success'] =\
            test.is_current_url(reverse("messages_index"))
    except Exception as e:
        print e
        parts[48]['test_message'] = str(e)
    
    
    # END OF ALL TESTS - cleanup
    mail.logout()
    return test.tear_down() 
    
    
def test_feedbacks():
    pass # TODO
    
    
    
    
    
    
    
    
    
