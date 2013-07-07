from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from datetime import datetime
from dateutil import parser
from dateutil.tz import tzutc
import urllib

from parse.decorators import session_comet
from parse import session as SESSION
from parse.utils import cloud_call, make_aware_to_utc
from parse.auth.decorators import login_required
from parse.apps.messages.models import Message
from parse.apps.messages import BASIC, OFFER, FEEDBACK, FILTERS
from apps.messages.forms import MessageForm
from parse.apps.accounts import sub_type
from repunch.settings import PAGINATION_THRESHOLD
from libs.repunch import rputils
from libs.dateutil.relativedelta import relativedelta


@login_required
def get_page(request):
    """
    Returns the corresponding chunk of rows in html to plug into
    the sent/feedback table.
    """
    if request.method == "GET" or request.is_ajax():
        type = request.GET.get("type")
        page = int(request.GET.get("page")) - 1
        if type == "sent":
            template = "manage/message_chunk.djhtml" 
            messages = SESSION.get_messages_sent_list(request.session)
            # sort
            header_map = {"date":"createdAt"}
            header = request.GET.get("header")
            if header: # header can only be date
                reverse = request.GET.get("order") == "desc"
                messages.sort(key=lambda r:\
                    r.__dict__[header_map[header]], reverse=reverse)
            
            # set the chunk
            start = page * PAGINATION_THRESHOLD
            end = start + PAGINATION_THRESHOLD
            data = {"messages":messages[start:end]}
            
            request.session["messages_sent_list"] = messages
            
        elif type == "feedback":
            template = "manage/feedback_chunk.djhtml"
            feedbacks = SESSION.get_messages_received_list(request.session)
            # sort
            header_map = {
                "feedback-date": "createdAt",
                "feedback-from": "sender_name", 
            }
            header = request.GET.get("header")
            if header:
                reverse = request.GET.get("order") == "desc"
                feedbacks.sort(key=lambda r:\
                    r.__dict__[header_map[header]], reverse=reverse)
                    
            request.session["messages_received_list"] = feedbacks
            
            # set the chunk
            start = page * PAGINATION_THRESHOLD 
            end = start + PAGINATION_THRESHOLD
            data = {"feedback":feedbacks[start:end]}
        
        return render(request, template, data)
        
    return HttpResponse("Bad request")


@login_required
@session_comet  
def index(request):
    data = {'messages_nav': True}
    
    messages = SESSION.get_messages_sent_list(request.session)
    feedbacks = SESSION.get_messages_received_list(request.session)
        
    # initially display the first 20 messages/feedback chronologically
    messages.sort(key=lambda r: r.createdAt, reverse=True)
    feedbacks.sort(key=lambda r: r.createdAt, reverse=True)
    
    data['messages'] = messages[:PAGINATION_THRESHOLD]
    data['feedback'] = feedbacks[:PAGINATION_THRESHOLD]
        
    data["pag_threshold"] = PAGINATION_THRESHOLD
    data["pag_page"] = 1
    data["sent_count"] = len(messages)
    data["feedback_count"] = len(feedbacks)
    
    if SESSION.get_patronStore_count(request.session):
        data['has_patrons'] = True
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/messages.djhtml', data)


@login_required
@session_comet  
def edit(request, message_id):
    store = SESSION.get_store(request.session)

    data = {'messages_nav': True, 'message_id': message_id,
        "filters": FILTERS}
        
    # for slider most_loyal min_punches
    mp = store.get("patronStores", limit=1,
        order="-all_time_punches")[0].get('all_time_punches')
    # make sure cache attr is None for future queries!
    store.patronStores = None
    
    data['mp_slider_value'] = int(mp*0.50)
    data['mp_slider_min'] = int(mp*0.20)
    data['mp_slider_max'] = int(mp*0.80)
    
    if request.method == 'POST' or (request.method == "GET" and\
        request.GET.get("send_message")):
        
        # 404 if no patrons 
        if not store.get("patronStores", count=1, limit=0):
            raise Http404
            
        if (request.method == "GET" and request.GET.get("send_message")):
            postDict = request.session['message_b4_upgrade'].copy()
            # cleanup temp vars in session
            del request.session['message_b4_upgrade']
            del request.session['from_limit_reached']
        else:
            postDict = request.POST.dict().copy()
        
        form = MessageForm(postDict) 
        subType = SESSION.get_subscription(\
                    request.session).get('subscriptionType')
        # refresh the message count - make sure we get the one in the cloud
        del request.session['message_count']
        message_count = SESSION.get_message_count(request.session)
                                
        limit_reached = message_count >= sub_type[subType]['max_messages']
        
        if form.is_valid() and not limit_reached:
            # create the message
            message = Message(sender_name=\
                    store.get('store_name'), store_id=store.objectId)
            message.update_locally(postDict, False)
            
            # check if attach offer is selected
            if 'attach_offer' in postDict:
                d = parser.parse(postDict['date_offer_expiration'])
                d = make_aware_to_utc(d, 
                    SESSION.get_store_timezone(request.session))
                message.set('date_offer_expiration', d)
                message.set('message_type', OFFER)
                message.set("offer_redeemed", False)
            else:
                # pop the offer
                message.set('offer_title', None)
                message.set('date_offer_expiration', None)
                # already defaults to None but whatever.
                message.set("offer_redeemed", None)
                message.set('message_type', BASIC)
                
            message.create()
            data['message'] = message
            # add to the store's relation
            store.add_relation("SentMessages_", [message.objectId]) 
            success_message = "Message has been sent."
            
            # update messages_sent_list in session cache
            messages_sent_list = SESSION.get_messages_sent_list(\
                request.session)
            messages_sent_list.insert(0, message)
            request.session['messages_sent_list'] =\
                messages_sent_list
                
            # update the message_count
            message_count += 1
            request.session['message_count'] = message_count

            params = {
                "store_id":store.objectId,
                "store_name":store.get('store_name'),
                "subject":message.get('subject'),
                "message_id":message.objectId,
                "filter":message.filter,
            }

            if msg_filter == "idle":
                d = timezone.now() + relativedelta(days=-21)
                params.update({"idle_date":d.isoformat()})
            elif msg_filter == "most_loyal":
                params.update({"min_punches":\
                    postDict['min_punches']})

            # push notification
            cloud_call("retailer_message", params)
            
            # update store session cache
            request.session['store'] = store

            return HttpResponseRedirect(message.get_absolute_url())
            
        elif limit_reached and subType != 2:
            data['limit_reached'] = limit_reached
            # save the dict to the session
            request.session['message_b4_upgrade'] =\
                request.POST.dict().copy()
        elif limit_reached and subType == 2:
            data['limit_reached'] = limit_reached
            data['maxed_out'] = True
        elif 'min_punches' in form.errors:
            data['error'] = "Minimum punches must be a "+\
                                "whole number."
        else:
            data['error'] = "The form you submitted has errors."
    else:
        # check if the incoming request is for an account upgrade
        do_upgrade = request.GET.get("account_upgrade") 
        if do_upgrade and do_upgrade.isdigit() and\
            int(do_upgrade) == 1:
            # flag the upgrade view
            request.session["from_limit_reached"] = True
            # redirect to upgrade account 
            return HttpResponseRedirect(reverse("account_upgrade"))
            
        if message_id in (0, '0'):
            form = MessageForm()
        else:
            if request.GET.get("error"):
                data['error'] = request.GET.get("error")
            if request.GET.get("success"):
                data['success'] = request.GET.get("success")
            
            # get from the messages_sent_list in session cache
            messages_sent_list = SESSION.get_messages_sent_list(\
                request.session)
            request.session['messages_sent_list'] =\
                messages_sent_list
            for m in messages_sent_list:
                if m.objectId == message_id:
                    data['message'] = m
            if data['message']:
                form = MessageForm(data['message'].__dict__.copy())
            else:
                form = MessageForm()
           
    # update store session cache
    request.session['store'] = store
            
    data['form'] = form

    return render(request, 'manage/message_edit.djhtml', data)

@login_required
@session_comet  
def details(request, message_id):
    # get from the messages_sent_list in session cache
    messages_sent_list = SESSION.get_messages_sent_list(\
        request.session)
    message = None
    for m in messages_sent_list:
        if m.objectId == message_id:
            message = m
    if not message:
        raise Http404
    return render(request, 'manage/message_details.djhtml', 
            {'message':message, 'messages_nav': True,
                "filters":FILTERS})


# FEEDBACK ------------------------------------------
@login_required
@session_comet  
def feedback(request, feedback_id):
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
        raise Http404
    
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

@login_required
@session_comet  
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
        raise Http404
        
    # first fetch the feedback - make sure that we have the updated
    # one - not the one in the cache
    if not feedback.fetchAll(): # it has been deleted
        # remove feedback from the session
        messages_received_list.pop(i_remove)
        request.session['messages_received_list'] =\
            messages_received_list
        return redirect(reverse('messages_index') +\
                        "?%s" % urllib.urlencode({'error':\
                        'Feedback has been deleted elsewhere.'}))
    
    if request.method == 'POST':
        body = request.POST.get('body')
        if body == None or len(body) == 0:
            data['error'] = 'Please enter a message.'  
        elif len(body) > 750:
            data['error'] = 'Body must be less than 750 characters.' 
            data['body'] = body
        # double check if feedback already has a reply
        # should not go here unless it is a hacker 
        elif feedback.get('Reply'):
            data['error']='This feedback has already been replied to.'
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

            # push notification
            cloud_call("retailer_message", {
                "store_id":store.objectId,
                "store_name":store.get('store_name'),
                "subject":feedback.get('subject'),
                "message_id":feedback.objectId,
                "filter":'one',
                "patron_id":feedback.get('patron_id'),
            })

            return redirect(reverse('feedback_details', 
                        args=(feedback.objectId,)) +\
                        "?%s" % urllib.urlencode({'success':\
                        'Reply has been sent.'}))
    else:
        data['from_address'] = store.get("store_name")
        data['subject'] = 'Re: ' + feedback.get('subject')
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

@login_required
@session_comet  
def feedback_delete(request, feedback_id):
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
        raise Http404

    # delete reply to message first if exist
    if feedback.get('Reply'):
        feedback_reply = feedback.get('reply')
        feedback_reply.delete()
    
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
    
    feedback.delete()
    return redirect(reverse('messages_index')+ "?%s" % urllib.urlencode({'success': 'Feedback has been deleted.'}))

@login_required
def delete(request, message_id):
    # entire thing is commented out just in case they try to trigger
    # this via the url manually
    """ this should not be used as messages, once sent, 
    cannot be deleted. """
    """
    store = request.session['account'].store
    
    message = store.get("sentMessages", objectId=message_id)[0]
    if not message:
        raise Http404

    # delete reply to message first if exist
    # there shouldn't be any from messages sent by store
    # except if it is a reply to a feedback but just to be safe
    if message.get('Reply'):
        msg_reply = message.get('reply')
        msg_reply.delete()
    
    message.delete()
    return redirect(reverse('messages_index')+\
            "?%s" % urllib.urlencode({'success':\
            'Message has been deleted.'}))
    """
    return HttpResponse("sorry, this operation is not supported")

