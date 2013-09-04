"""
Selenium tests for dashboard 'Messages' tab.
"""

from django.core.urlresolvers import reverse
from django.utils import timezone
from selenium.webdriver.common.keys import Keys
from time import sleep
from urllib import urlencode

from libs.dateutil.relativedelta import relativedelta
from libs.imap import Mail
from tests import SeleniumTest
from apps.messages.forms import DATE_PICKER_STRFTIME
from parse.apps.accounts.models import Account
from parse.notifications import EMAIL_UPGRADE_SUBJECT
from parse.utils import cloud_call
from parse.apps.messages import FEEDBACK
from repunch.settings import COMET_PULL_RATE

TEST_USER = {
    "username": "clothing@vandolf.com",
    "password": "123456",
}

# IMPORTANT! This patron must have a PatronStore with the store above!
TEST_PATRON = {
    "username": "kira@vandolf.com",
    "password": "123456",
}

def test_messages():
    # TODO test that patrons are getting the messages!!!
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
            
    store.set("sentMessages", None)
            
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
        "section_name": "Sending messages works?",
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
        ("#login_username", TEST_USER['username']),
        ("#login_password", TEST_USER['password']),
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
        test.find("#update-form-submit").click()
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
        test.find("#update-form-submit").click()
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
    """
    This test also tests cloud code send_feedback.
    """
    # we can clear the list locally but just re-pull from parse
    account = Account.objects().get(username=TEST_USER['username'],
        include="Store.Subscription")
    store = account.store
    subscription = store.subscription
    
    
    account = Account.objects().get(username=TEST_PATRON['username'],
        include="Patron")
    patron = account.patron
        
    # make sure that the account is not used for these tests
    account = None
    
    # clear the received messages relation
    received_messages = store.get("receivedMessages", keys="")
    if received_messages:
        store.remove_relation("ReceivedMessages_",
            [m.objectId for m in received_messages])
            
    store.set("receivedMessages", None)
 
    test = SeleniumTest()
    parts = [
        {'test_name': "User needs to be logged in to access page"},
        {'test_name': "Cloud code send_feedback works"},
        {'test_name': "Notification badge appears if there are" +\
            " unread feedbacks"},
        {'test_name': "A new row appears when feedback is received"},
        {'test_name': "Feedback is initially unread (dashboard)"},
        {'test_name': "Feedback is in store's ReceivedMessages " +\
            "relation and is initially unread"},
        {'test_name': "Clicking the row redirects user to the " +\
            "feedback detail page"},
        {'test_name': "Clicking back to feedback inbox redirects " +\
            "user back to messages index with feedback tab active"},
        {'test_name': "Feedback is now read (dashboard)"},
        {'test_name': "Feedback is now read (Parse)"},
        {'test_name': "Clicking reply redirects user to feedback " +\
            "reply page"},
        {'test_name': "Reply body is required."},
        {'test_name': "Replying redirects user back to feedback " +\
            "details"},
        {'test_name': "The reply is visible"},
        {'test_name': "The reply message is saved in the store's " +\
            "sent messages relation with message_type of feedback"},
        {'test_name': "The reply message is saved in the Patron's " +\
            "received messages relation wrapped in a Message Status"},
        {'test_name': "A feedback with a reply does not have a " +\
            "reply button"},
        {'test_name': "Clicking delete message prompts the user " +\
            "to confirm the deletion"},
        {'test_name': "The user is redirected to messages index " +\
            "with feedback tab active"},
        {'test_name': "Deleting the reply only removes the message" +\
            " from the store's sent messages relation"},
        {'test_name': "The deleted feedback is no longer in " +\
            "the table"},
        {'test_name': "Multiple feedbacks (testing 3 here) " +\
            "can appear at the same time"},
    ]
    section = {
        "section_name": "Receiving messages works?",
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
        ("#login_username", TEST_USER['username']),
        ("#login_password", TEST_USER['password']),
        ("", Keys.RETURN)
    )
    test.action_chain(0, selectors, "send_keys") # ACTION!
    sleep(5) 
    
    def send_feedback(subject, body):
        """ This is a consumer action - not dashboard """
        return cloud_call("send_feedback", {
            "store_id": store.objectId,
            "patron_id": patron.objectId,
            "sender_name": patron.get_fullname(),
            "subject": subject,
            "body": body,
        })
    
    def feedback_id(feedback_tr):
        return feedback_tr.find_element_by_css_selector(\
            "a").get_attribute("href").split("/")[-1]
        
    def feedback_unread(feedback_tr):
        """ check parse if the fb is unread """
        fb_id = feedback_id(feedback_tr)
        store.set("receivedMessages", None)
        msg = store.get("receivedMessages", objectId=fb_id)
        if msg and len(msg) > 0:
           return not msg[0].is_read
        
        return False
        
    ##########  Cloud code send_feedback works
    try:
        parts[1]['success'] = send_feedback("feedback #1",
            "body #1").get("result") == "success"
    except Exception as e:
        print e
        parts[1]['test_message'] = str(e)
        
    ##########  Notification badge appears if there are
    ###         unread feedbacks
    try:
        sleep(COMET_PULL_RATE*2 + 2)
        parts[2]['success'] = test.element_exists("#messages-nav " +\
            "a div.nav-item-badge")
    except Exception as e:
        print e
        parts[2]['test_message'] = str(e)
    
    ##########  A new row appears when feedback is received 
    try:
        test.find("#tab-feedback").click()
        feedbacks =\
            test.find("#tab-body-feedback div.tr", multiple=True)
        parts[3]['success'] = len(feedbacks) > 0
    except Exception as e:
        print e
        parts[3]['test_message'] = str(e)
    ##########  Feedback is initially unread (dashboard)
    try:
        parts[4]['success'] =\
            feedbacks[0].get_attribute("class").__contains__("unread")
    except Exception as e:
        print e
        parts[4]['test_message'] = str(e)
    
    ##########  Feedback is in store's ReceivedMessages
    ###         relation and is initially unread 
    try:
        parts[5]['success'] = feedback_unread(feedbacks[0])
    except Exception as e:
        print e
        parts[5]['test_message'] = str(e)
    ##########  Clicking the row redirects user to the 
    ###         feedback detail page
    try:
        fb_id = feedback_id(feedbacks[0])
        feedbacks[0].find_element_by_css_selector("a").click()
        sleep(2)
        parts[6]['success'] = test.is_current_url(reverse(\
            "feedback_details", args=(fb_id,)))
    except Exception as e:
        print e
        parts[6]['test_message'] = str(e)
    ##########  Clicking back to feedback inbox redirects 
    ###         user back to messages index with feedback tab active 
    try:
        test.find("#back_to_feedback").click()
        sleep(1)
        parts[7]['success'] =\
            test.find("#tab-feedback").get_attribute(\
            "class").__contains__("active")
    except Exception as e:
        print e
        parts[7]['test_message'] = str(e)
    ##########  Feedback is now read (dashboard) 
    try:
        feedbacks =\
            test.find("#tab-body-feedback div.tr", multiple=True)
        parts[8]['success'] =  not feedbacks[0].get_attribute(\
            "class").__contains__("unread")
    except Exception as e:
        print e
        parts[8]['test_message'] = str(e)
    ##########  Feedback is now read (Parse)
    try:
        parts[9]['success'] = not feedback_unread(feedbacks[0])
    except Exception as e:
        print e
        parts[9]['test_message'] = str(e)
    ##########  Clicking reply redirects user to feedback reply page
    try:
        fb_id = feedback_id(feedbacks[0])
        feedbacks[0].find_element_by_css_selector("a").click()
        sleep(2)
        test.find("#reply-button").click()
        sleep(1)
        parts[10]['success'] = test.is_current_url(reverse(\
            "feedback_reply", args=(fb_id,)))
    except Exception as e:
        print e
        parts[10]['test_message'] = str(e)
    ##########  Reply body is required. 
    try:
        test.find("#body").send_keys("     ")
        test.find("#reply-form-submit").click()
        sleep(2)
        parts[11]['success'] = test.find("div.notification.hide " +\
            "div").text == "Please enter a message."
    except Exception as e:
        print e
        parts[11]['test_message'] = str(e)
    ##########  Replying redirects user back to feedback details
    try:
        test.find("#body").send_keys("Hey")
        test.find("#reply-form-submit").click()
        parts[12]['success'] = test.is_current_url(reverse(\
            "feedback_details", args=(fb_id,)) +\
            "?%s" % urlencode({'success':\
            'Reply has been sent.'}))
        sleep(5)
    except Exception as e:
        print e
        parts[12]['test_message'] = str(e)
    ##########  The reply is visible
    try:
        parts[13]['success'] = test.find("#reply-box " +\
            "div.sect.body").text == "Hey"
    except Exception as e:
        print e
        parts[13]['test_message'] = str(e)
    ##########  The reply message is saved in the store's 
    ###         sent messages relation with message_type of feedback
    try:
        test.find("#back_to_feedback").click()
        sleep(1)
        store.set("sentMessages", None)
        store.set("receivedMessages", None)
        parts[14]['success'] = len(store.get("sentMessages",
            objectId=store.get("receivedMessages", 
            objectId=fb_id)[0].Reply, message_type=FEEDBACK)) > 0
    except Exception as e:
        print e
        parts[14]['test_message'] = str(e)
    ##########  The reply message is saved in the Patron's 
    ###         received messages relation wrapped in a Message Status 
    try:
        patron.set("receivedMessages", None)
        parts[15]['success'] = len(patron.get("receivedMessages",
            Message=fb_id)) > 0
    except Exception as e:
        print e
        parts[15]['test_message'] = str(e)
    ##########  A feedback with a reply does not have a reply button
    try:
        feedbacks =\
            test.find("#tab-body-feedback div.tr", multiple=True)
        feedbacks[0].find_element_by_css_selector("a").click()
        sleep(2)
        parts[16]['success'] = not test.element_exists(\
            "#reply-form-submit")
    except Exception as e:
        print e
        parts[16]['test_message'] = str(e)
    ##########  Clicking delete message prompts the user 
    ###         to confirm the deletion
    try:
        test.find("#delete-button").click()
        sleep(1)
        alert = test.switch_to_alert()
        parts[17]['success'] = alert.text ==\
            "Are you sure you want to delete this feedback thread?"
    except Exception as e:
        print e
        parts[17]['test_message'] = str(e)
    ##########  The user is redirected to messages index 
    ###         with feedback tab active
    try:
        alert.accept()
        sleep(4)
        parts[18]['success'] =\
            test.find("#tab-feedback").get_attribute(\
            "class").__contains__("active")
    except Exception as e:
        print e
        parts[18]['test_message'] = str(e)
    ##########  Deleting the reply only removes the message
    ###         from the store's sent messages relation 
    try:
        store.set("receivedMessages", None)
        parts[19]['success'] = not store.get("receivedMessages",
            objectId=fb_id, message_type=FEEDBACK)
    except Exception as e:
        print e
        parts[19]['test_message'] = str(e)
    ##########  The deleted feedback is no longer in the table 
    try:
        test.find("#tab-feedback").click()
        sleep(1)
        feedbacks =\
            test.find("#tab-body-feedback div.tr a[href='%s']" %\
                (fb_id,), multiple=True)
        parts[20]['success'] = len(feedbacks) == 0
    except Exception as e:
        print e
        parts[20]['test_message'] = str(e)
    ##########  Multiple feedbacks (testing 3 here) 
    ###         can appear at the same time 
    try:
        send_feedback("feedback #2", "body #2")
        send_feedback("feedback #3", "body #3")
        send_feedback("feedback #4", "body #4")
        sleep(COMET_PULL_RATE*3 + 4)
        feedbacks =\
            test.find("#tab-body-feedback div.tr a", multiple=True)
        parts[21]['success'] = len(feedbacks) == 3
    except Exception as e:
        print e
        parts[21]['test_message'] = str(e)
    
    
    # END OF ALL TESTS - cleanup
    return test.tear_down() 
    
    
    
