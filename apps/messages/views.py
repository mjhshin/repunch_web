"""
Views for the Messages tab in the dashboard.
"""

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.sessions.backends.cache import SessionStore
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from datetime import datetime
from dateutil import parser
from dateutil.tz import tzutc
from math import ceil
import urllib, json

from parse.comet import comet_receive
from parse import session as SESSION
from parse.utils import cloud_call, make_aware_to_utc
from parse.decorators import access_required, admin_only
from parse.auth.decorators import login_required, dev_login_required
from parse.apps.messages.models import Message
from parse.apps.messages import BASIC, OFFER, FEEDBACK, FILTERS
from apps.messages.forms import MessageForm
from parse.apps.accounts import sub_type
from repunch.settings import PAGINATION_THRESHOLD, DEBUG,\
PRODUCTION_SERVER, COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY
from libs.repunch import rputils
from libs.dateutil.relativedelta import relativedelta

@dev_login_required
@login_required
@access_required(http_response="<div class='tr'>Access denied</div>",\
content_type="text/html")
def get_page(request):
    """
    Returns the corresponding chunk of rows in html to plug into
    the sent/feedback table.
    """
    
    if request.method == "GET":
        type = request.GET.get("type")
        page = int(request.GET.get("page")) - 1
        
        if type == "sent":
            # we will be rendering the message chunk template
            template = "manage/message_chunk.djhtml" 
            # retrieve the messages sent from our session cache
            messages = SESSION.get_messages_sent_list(request.session)
            # our input is called "date" which translates to "createdAt"
            header_map = {"date":"createdAt"}
            header = request.GET.get("header")
            
            # header can only be date at the moment
            if header: 
                # sort the messages based on given order
                reverse = request.GET.get("order") == "desc"
                messages.sort(key=lambda r:\
                    r.__dict__[header_map[header]], reverse=reverse)
            
            # insert the messages chunk in the template data
            start = page * PAGINATION_THRESHOLD
            end = start + PAGINATION_THRESHOLD
            data = {"messages":messages[start:end]}
            
            # save our reordered messages 
            request.session["messages_sent_list"] = messages
            
        elif type == "feedback":
            # we will be rendering the feedback chunk template
            template = "manage/feedback_chunk.djhtml"
            # retrieve the feedbacks from our session cache.
            feedbacks = SESSION.get_messages_received_list(request.session)
            
            # our inputs can be "feedback-date" mapping to "createdAt"
            # or "feedback-from" mapping to "sender_name"
            header_map = {
                "feedback-date": "createdAt",
                "feedback-from": "sender_name", 
            }
            header = request.GET.get("header")
            if header: 
                # sort the feedbacks based on the attribute and order
                reverse = request.GET.get("order") == "desc"
                feedbacks.sort(key=lambda r:\
                    r.__dict__[header_map[header]], reverse=reverse)
                    
            # insert the feedbacks chunk in the template data
            start = page * PAGINATION_THRESHOLD 
            end = start + PAGINATION_THRESHOLD
            data = {"feedback":feedbacks[start:end]}
            
            # save our reordered feedbacks
            request.session["messages_received_list"] = feedbacks
        
        # render our template with the feedback/messages sent chunks
        return render(request, template, data)
        
    # only GET methods are accepted here
    return HttpResponse("Bad request")


@dev_login_required
@login_required
@access_required
def index(request):
    """
    Render the messages template.
    """
    messages = SESSION.get_messages_sent_list(request.session)
    feedbacks = SESSION.get_messages_received_list(request.session)
        
    # initially display the first 20 messages/feedback chronologically
    messages.sort(key=lambda r: r.createdAt, reverse=True)
    feedbacks.sort(key=lambda r: r.createdAt, reverse=True)
    
    # prepare our template context variables use in our messages template
    data = {
        'messages_nav': True,
        'messages': messages[:PAGINATION_THRESHOLD],
        'feedback': feedbacks[:PAGINATION_THRESHOLD],
        'pag_threshold': PAGINATION_THRESHOLD,
        'pag_page': 1,
        'sent_count': len(messages),
        'feedback_count': len(feedbacks),
        'tab_feedback': request.GET.get('tab_feedback'),
    }
    
    if SESSION.get_patronStore_count(request.session):
        data['has_patrons'] = True
    
    # inserting this success and error message into the template
    # should be done in a cleaner way - this was done by the first guy
    # I just didn't bother changing it.
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/messages.djhtml', data)

@dev_login_required
@login_required
@admin_only(reverse_url="messages_index")
def message_no_limit(request):
    """
    Inserts a token in the dev session that allows bypass of message
    sending limits.
    """
    
    # this is only available in development - should use our
    # parse.decorators.dev_only decorator instead of this
    if PRODUCTION_SERVER:
        raise Http404 

    # insert the token in the session and return a plaintext response
    # confirming the success of the operation
    if request.method == "GET":
        request.session["message_limit_off"] = True
        return HttpResponse("Limit for sending messages has been turned off." +\
            "To turn it back on, please log out and log back in.")
    
    # only accept GET methods    
    return HttpResponse("Bad Request")

@dev_login_required
@login_required
@admin_only(reverse_url="messages_index")
def edit(request, message_id):
    """
    Render the message edit template for a new message and handles
    send message forms.
    """
    data = {
        'messages_nav': True,
        'message_id': message_id,
        "filters": FILTERS
    }
        
    store = SESSION.get_store(request.session)
    # number of patron stores
    mp = SESSION.get_patronStore_count(request.session)
    # make sure cache attr is None for future queries!
    store.patronStores = None
    
    data['mp_slider_value'] = int(ceil(float(mp)*0.50))
    data['mp_slider_min'] = 1
    data['mp_slider_max'] = mp
    
    # redirect if no patrons 
    if not store.get("patronStores", count=1, limit=0):
        return redirect(reverse("messages_index"))
    
    # user submitted a form by form submission through POST request
    # or user is coming from an upgrade sequence from subscription_update
    if request.method == 'POST' or (request.method == "GET" and\
        request.GET.get("send_message") and "message_b4_upgrade" in\
        request.session):
        
        if request.method == "GET":
            # user is coming from an upgrade sequence from subscription_update
            postDict = request.session['message_b4_upgrade'].copy()
            # cleanup temp vars in session
            del request.session['message_b4_upgrade']
            del request.session['from_limit_reached']
            
        else:
            # user submitted a form by form submission through POST request
            postDict = request.POST.dict().copy()
        
        # populate a message form with the POST data for validation
        form = MessageForm(postDict) 
        
        if form.is_valid():
            # form is valid so continue to send the message
            subscription = SESSION.get_subscription(request.session)
            subType = subscription.get('subscriptionType')
        
            # refresh the message count - make sure we get the one in the cloud
            if 'message_count' in request.session:
                del request.session['message_count']
            message_count = SESSION.get_message_count(request.session)
            
            # get the max_messages from the user's subscriptionType
            # or the highest level if god_mode is on
            if subscription.god_mode:
                max_messages = sub_type[2]['max_messages']
            else:
                max_messages = sub_type[subType]['max_messages']
            
            # limit is reached if the amount of messages sent this
            # billing cycle passed the amount for that subscription type                                    
            limit_reached = message_count >= max_messages
            
            # We always enforce the limit when we are in production
            # otherwise, we ignore it if we have message_limit_off in our session
            if limit_reached and (PRODUCTION_SERVER or\
                (not PRODUCTION_SERVER and "message_limit_off" not in request.session)):
                
                data['limit_reached'] = limit_reached
                
                # not the highest level of subscription so an upgrade
                # is still possible
                if subType != 2:
                    # save the dict to the session
                    request.session['message_b4_upgrade'] =\
                        request.POST.dict().copy()
                        
                # the highest level of subscription so no more
                # upgrades can occur - therefore maxed_out
                elif subType == 2:
                    data['maxed_out'] = True
                    
            else:
                # limit has not yet been reached - send the message
                # build the message from session and POST data
                message = Message(\
                    sender_name=store.get('store_name'),
                    store_id=store.objectId
                )
                message.update_locally(postDict, False)
                
                
                # check if attach offer is selected
                if 'attach_offer' in postDict:
                    # message has an offer - extract it from the post
                    # post data ensuring proper datetime format
                    d = parser.parse(postDict['date_offer_expiration'])
                    d = make_aware_to_utc(d, 
                        SESSION.get_store_timezone(request.session))
                    message.set('date_offer_expiration', d)
                    message.set('message_type', OFFER)
                    
                else:
                    # make sure to delete offer information in the case
                    # that attach offer is not checked but the form
                    # submitted still contained offer information
                    message.set('offer_title', None)
                    message.set('date_offer_expiration', None)
                    message.set('message_type', BASIC)
                    
                # actually create the message to Parse
                message.create()
                
                # put the message in the template context for rendering
                data['message'] = message
                # add to the store's relation
                store.add_relation("SentMessages_", [message.objectId]) 

                # prepare the parameters for the cloud call
                params = {
                    "store_id":store.objectId,
                    "store_name":store.get('store_name'),
                    "subject":message.get('subject'),
                    "message_id":message.objectId,
                    "filter":message.filter,
                }
                
                # process the filter option
                if message.filter == "idle":
                    # pass in the correct idle_date which is today
                    # minus the days specified by idle_latency
                    idle_days = postDict['idle_latency']
                    d = timezone.now() + relativedelta(days=\
                        -1*int(idle_days))
                    params.update({"idle_date":d.isoformat()})
                    
                elif message.filter == "most_loyal":
                    # pass in the number of patrons
                    params.update({"num_patrons": postDict['num_patrons']})
                        
                # update store and message_count in session cache
                request.session['message_count'] = message_count
                request.session['store'] = store
                # save session- cloud_call may take a while!
                request.session.save()

                # make the cloud call
                res = cloud_call("retailer_message", params)
                if "error" not in res and res.get("result"):
                    message.set("receiver_count",
                        res.get("result").get("receiver_count"))
                        
                # notify other tabs and windows that are logged into
                # this store about the new message sent.
                payload = {
                    COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                    "newMessage":message.jsonify()
                }
                comet_receive(store.objectId, payload)
                
                # Note that the new message is saved in comet_receive
                # make sure we have the latest session to save!
                request.session.clear()
                request.session.update(SessionStore(request.session.session_key))

                return HttpResponseRedirect(message.get_absolute_url())
            
        elif 'num_patrons' in form.errors:
            # form is invalid due to the number of patrons input
            # for most_loyal filter
            data['error'] = "Number of customers must be a "+\
                                "whole number and greater than 0."
                                
        else:
            # form has some errors
            data['error'] = "The form you submitted has errors."
            
    else:
        # check if the incoming request is for an account upgrade
        if request.GET.get("do_upgrade"):
            # flag the upgrade view
            request.session["from_limit_reached"] = True
            # redirect to upgrade account 
            return HttpResponseRedirect(reverse("subscription_update") +\
                "?do_upgrade=1")
            
        if message_id in (0, '0'):
            # this is a new message so just instantiate a new form
            form = MessageForm()
            
        else:
            # this is an existing message that the user wants to view
        
            # inserting this success and error message into the template
            # should be done in a cleaner way - this was done by the 
            # first guy. I just didn't bother changing it.
            if request.GET.get("error"):
                data['error'] = request.GET.get("error")
            if request.GET.get("success"):
                data['success'] = request.GET.get("success")
            
            # get from the messages_sent_list in session cache
            messages_sent_list = SESSION.get_messages_sent_list(\
                request.session)
            for m in messages_sent_list:
                if m.objectId == message_id:
                    data['message'] = m
                    
            if data['message']:
                # message is found so fill up the form with its data
                form = MessageForm(data['message'].__dict__.copy())
                
            else:
                # message not found so just instantiate a new form
                form = MessageForm()
           
    # update store session cache
    request.session['store'] = store
            
    # inject the form in the template context for rendering
    data['form'] = form

    return render(request, 'manage/message_edit.djhtml', data)
    

@dev_login_required
@login_required
@access_required
def details(request, message_id):
    """
    Renders the message details template.
    """
    
    # get from the messages_sent_list in session cache
    messages_sent_list = SESSION.get_messages_sent_list(request.session)
    message = None
    for m in messages_sent_list:
        if m.objectId == message_id:
            message = m
            
    if not message:
        # message not found - assume that it was deleted sice we don't
        # use comet.js to remove deleted message client side
        return redirect(reverse('messages_index')+ "?%s" %\
             urllib.urlencode({'error':\
                'Message has already been deleted.'}))
                
    return render(request, 'manage/message_details.djhtml', 
            {'message':message, 'messages_nav': True,
                "filters":FILTERS})


# FEEDBACK ------------------------------------------
@dev_login_required
@login_required
@access_required
def feedback(request, feedback_id):
    """
    TODO
    """
    data = {'messages_nav': True, 'feedback_id':feedback_id,
             "store_name":\
                SESSION.get_store(request.session).get("store_name")}    
    
    # get from the messages_received_list in session cache
    messages_received_list = SESSION.get_messages_received_list(\
        request.session)
    i_remove, feedback = 0, None
    for ind, m in enumerate(messages_received_list):
        if m.objectId == feedback_id:
            feedback = m
            i_remove = ind
            break
            
    if not feedback:
        return redirect(reverse('messages_index')+ "?%s" %\
             urllib.urlencode({'error':\
                'Feedback has already been deleted.',
                "tab_feedback":1}))
    
    if not feedback.is_read:
        feedback.is_read = True
        feedback.update()
        
    # make sure that the message stored in the list is the updated 1
    messages_received_list.pop(i_remove)
    messages_received_list.insert(i_remove, feedback)
    request.session['messages_received_list'] = messages_received_list
        
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    # there should only be at most 1 reply
    data['reply'] = feedback.get('reply')
    data['feedback'] = feedback
    
    return render(request, 'manage/feedback.djhtml', data)

@dev_login_required
@login_required
@admin_only(reverse_url="messages_index", reverse_postfix="tab_feedback=1")
def feedback_reply(request, feedback_id):
    account = request.session['account']
    store = SESSION.get_store(request.session)
    data = {'messages_nav': True}
    
    # get from the messages_received_list in session cache
    messages_received_list = SESSION.get_messages_received_list(\
        request.session)
    i_remove, feedback = 0, None
    for ind, m in enumerate(messages_received_list):
        if m.objectId == feedback_id:
            feedback = m
            i_remove = ind
            break
            
    if not feedback:
        return redirect(reverse('messages_index')+ "?%s" %\
             urllib.urlencode({'error':\
                'Feedback has already been deleted.'}))
    
    if request.method == 'POST':
        body = request.POST.get('body')
        if body is not None:
            body = body.strip()
        else:
            body = ""
            
        data['body'] = body
        data['from_address'] = store.get("store_name")
        
        if len(body) == 0:
            data['error'] = 'Please enter a message.'  
        elif len(body) > 750:
            data['error'] = 'Body must be less than 750 characters.' 
        # double check if feedback already has a reply
        # should not go here unless it is a hacker 
        elif feedback.get('Reply'):
            return redirect(reverse('messages_index')+ "?%s" %\
                 urllib.urlencode({'error':\
                    'Feedback has already been replied to.'}))
        else:
            msg = Message.objects().create(message_type=\
                FEEDBACK, sender_name=store.get('store_name'),
                store_id=store.objectId, body=body)
            store.add_relation("SentMessages_", [msg.objectId])
            # set feedback Reply pointer to message
            feedback.set('Reply', msg.objectId)
            feedback.update()
            
            # store the updated feedback
            messages_received_list.pop(i_remove)
            messages_received_list.insert(i_remove, feedback)
            request.session['messages_received_list'] =\
                messages_received_list
                
            # save the session now! cloud_call may take a bit!
            request.session.save()

            # push notification
            cloud_call("retailer_message", {
                "store_id":store.objectId,
                "store_name":store.get('store_name'),
                "message_id":feedback.objectId,
                "filter":'one',
                "patron_id":feedback.get('patron_id'),
                "feedback_reply_body": body,
            })
            
            payload = {
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "newMessage":feedback.jsonify()
            }
            comet_receive(store.objectId, payload)
            
            # make sure we have the latest session to save!
            request.session.clear()
            request.session.update(SessionStore(request.session.session_key))

            return redirect(reverse('feedback_details', 
                        args=(feedback.objectId,)) +\
                        "?%s" % urllib.urlencode({'success':\
                        'Reply has been sent.'}))
    else:
        data['from_address'] = store.get("store_name")
        # if the user manually tweaks the url, then s/he might be
        # able to reply to a feedback that already has a reply.
        if feedback.get("Reply"):
            return redirect(reverse('feedback_details', 
                        args=(feedback.objectId,)) +\
                        "?%s" % urllib.urlencode({'error':\
                        'Cannot reply more than once.'})) 
        
    # update store session cache
    request.session['store'] = store
    data['feedback'] = feedback
    
    # store the updated feedback
    messages_received_list.pop(i_remove)
    messages_received_list.insert(i_remove, feedback)
    request.session['messages_received_list'] =\
        messages_received_list
    
    return render(request, 'manage/feedback_reply.djhtml', data)

@dev_login_required
@login_required
@admin_only(reverse_url="messages_index", reverse_postfix="tab_feedback=1")
def feedback_delete(request, feedback_id):
    store = SESSION.get_store(request.session)
    # get from the messages_received_list in session cache
    messages_received_list = SESSION.get_messages_received_list(\
        request.session)
    i_remove, feedback = 0, None
    for ind, m in enumerate(messages_received_list):
        if m.objectId == feedback_id:
            feedback = m
            i_remove = ind
            break
            
    if not feedback:
        return redirect(reverse('messages_index')+ "?%s" %\
             urllib.urlencode({'error':\
                'Feedback has already been deleted.'}))
                
    # DO NOT DELETE ANYTHING! Just remove from the store's relation
    store.remove_relation("ReceivedMessages_", [feedback.objectId])
    
    # update messages_received_list in session cache
    messages_received_list = SESSION.get_messages_received_list(\
        request.session)
    i_remove = 0
    for i, m in enumerate(messages_received_list):
        if m.objectId == feedback.objectId:
            i_remove = i
            break
    messages_received_list.pop(i_remove)
    request.session['messages_received_list'] =\
        messages_received_list
        
    # notify other dashboards of this change
    store_id = store.objectId
    deleted_feedback = Message(objectId=feedback.objectId)
    payload = {
        COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
        "deletedFeedback":deleted_feedback.jsonify(),
    }
    comet_receive(store.objectId, payload)
        
    # no need to save the store since we just removed from relation
        
    return redirect(reverse('messages_index')+ "?%s" %\
        urllib.urlencode({'success':'Feedback has been deleted.',
            'tab_feedback':1}))

@dev_login_required
@login_required
@admin_only(reverse_url="messages_index")
def delete(request, message_id):
    """ cannot delete a message! """
    return HttpResponse("error")

