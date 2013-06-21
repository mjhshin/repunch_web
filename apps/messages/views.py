from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from datetime import datetime
from dateutil import parser
from dateutil.tz import tzutc
import urllib

from parse import session as SESSION
from parse.utils import cloud_call
from parse.auth.decorators import login_required
from parse.apps.messages.models import Message
from parse.apps.messages import BASIC, OFFER, FEEDBACK, FILTERS
from apps.messages.forms import MessageForm
from parse.apps.accounts import sub_type
from libs.repunch import rputils
from libs.dateutil.relativedelta import relativedelta


@login_required
def index(request):
    rputils.set_timezone(request)
    data = {'messages_nav': True}
        
    data['messages'] = SESSION.get_messages_sent_list(request.session)
    data['feedback'] =\
                SESSION.get_messages_received_list(request.session)
    
    if SESSION.get_patronStore_count(request.session):
        data['has_patrons'] = True
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/messages.djhtml', data)


@login_required
def edit(request, message_id):
    rputils.set_timezone(request)
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
    
    if request.method == 'POST':
        # 404 if no patrons 
        if not store.get("patronStores", count=1, limit=0):
            raise Http404
        form = MessageForm(request.POST) 
        # check here if limit has been reached
        start = datetime.now().replace(day=1, hour=0,
                                    minute=0, second=0)
        subType = SESSION.get_subscription(\
                    request.session).get('subscriptionType')
        num_sent = store.get('sentMessages', createdAt__gte=start,
                                count=1, limit=0)
        request.session['message_count'] = num_sent
                                
        limit_reached = num_sent >= sub_type[subType]['max_messages']
        
        if form.is_valid() and not limit_reached:
            if form.data.get('action')  == 'upgrade':
                pass
                """
                if account.upgrade():
                    message.status = 'Sent'
                    message.date_sent = datetime.date.today()
                    request.session['account'] = account 
                else:
                    data['error'] = "Error upgrading your account."
                """

            # create the message
            message = Message.objects().create(sender_name=\
                    store.get('store_name'), store_id=store.objectId)
            message.update_locally(request.POST.dict(), False)
            
            # check if attach offer is selected
            if 'attach_offer' in request.POST.dict():
                d = parser.parse(\
                    request.POST['date_offer_expiration'])
                # make aware
                d = timezone.make_aware(d, 
                    SESSION.get_store_timezone(request.session))
                # then convert to utc format
                d = timezone.localtime(d, tzutc())
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

            message.update()
            data['message'] = message
            # add to the store's relation
            store.add_relation("SentMessages_", [message.objectId]) 
            success_message = "Message has been sent."
            
            # update messages_sent_list in session cache
            messages_sent_list = SESSION.get_messages_sent_list(\
                request.session)
            messages_sent_list.append(message)
            request.session['messages_sent_list'] =\
                messages_sent_list

            msg_filter = request.POST['chosen_filter']
            params = {
                "store_id":store.objectId,
                "store_name":store.get('store_name'),
                "subject":message.get('subject'),
                "message_id":message.objectId,
                "filter":msg_filter,
            }

            if msg_filter == "idle":
                d = datetime.now() + relativedelta(days=-21)
                params.update({"idle_date":d.isoformat()})
            elif msg_filter == "most_loyal":
                params.update({"min_punches":\
                    request.POST['min_punches']})

            # push notification
            cloud_call("retailer_message", params)
            
            # update store session cache
            request.session['store'] = store

            return HttpResponseRedirect(message.get_absolute_url())
            
        elif limit_reached and subType != 2:
            data['limit_reached'] = limit_reached
        elif limit_reached and subType == 2:
            data['limit_reached'] = limit_reached
            data['maxed_out'] = True
        elif 'min_punches' in form.errors:
            data['error'] = "Minimum punches must be a "+\
                                "whole number."
        else:
            data['error'] = "The form you submitted has errors."
    else:
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
            form = MessageForm(data['message'].__dict__.copy())
           
    # update store session cache
    request.session['store'] = store
            
    data['form'] = form

    return render(request, 'manage/message_edit.djhtml', data)

@login_required
def details(request, message_id):
    rputils.set_timezone(request)
    # get from the messages_sent_list in session cache
    messages_sent_list = SESSION.get_messages_sent_list(\
        request.session)
    request.session['messages_sent_list'] =\
        messages_sent_list
    for m in messages_sent_list:
        if m.objectId == message_id:
            message = m
    
    if not message:
        raise Http404
    """
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    date_offer_expiration = None
    if message.date_offer_expiration:
        date_offer_expiration = message.date_offer_expiration.replace(tzinfo=from_zone)
        date_offer_expiration = date_offer_expiration.astimezone(to_zone)
    """
    return render(request, 'manage/message_details.djhtml', 
            {'message':message, 'messages_nav': True})

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

# FEEDBACK ------------------------------------------
@login_required
def feedback(request, feedback_id):
    account = request.session['account']
    store = SESSION.get_store(request.session)
    data = {'messages_nav': True, 'feedback_id':\
            feedback_id, 'account_username':\
            account.get('username')}    
    
    feedback = store.get("receivedMessages", objectId=feedback_id)[0]
    # make sure cache attr is None for future queries!
    store.receivedMessages = None
    if not feedback:
        raise Http404
    
    if not feedback.is_read:
        feedback.is_read = True
        feedback.update()
        
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
        
    # update store session cache
    request.session['store'] = store
    
    # there should only be at most 1 reply
    data['reply'] = feedback.get('reply')
    data['feedback'] = feedback
    
    return render(request, 'manage/feedback.djhtml', data)

@login_required
def feedback_reply(request, feedback_id):
    account = request.session['account']
    store = SESSION.get_store(request.session)
    data = {'messages_nav': True}    
    
    feedback = store.get("receivedMessages", objectId=feedback_id)[0]
    # make sure cache attr is None for future queries!
    store.receivedMessages = None
    if not feedback:
        raise Http404
    
    if request.method == 'POST':
        body = request.POST.get('body')
        if body == None or len(body) == 0:
            data['error'] = 'Please enter a message.'   
        # double check if feedback already has a reply
        # should not go here unless it is a hacker 
        elif feedback.get('Reply'):
            data['error'] = 'You cannot reply more than once to a '+\
                                'feedback.'
        else:
            # create BASIC message no subject
            msg = Message.objects().create(message_type=\
                BASIC, sender_name=store.get('store_name'),
                store_id=store.objectId, body=body)
            # add to ReceivedMessages relation
            store.add_relation("ReceivedMessages_", [msg.objectId])
            # set feedback Reply pointer to message
            feedback.set('Reply', msg.objectId)
            feedback.update()

            # push notification
            cloud_call("retailer_message", {
                "store_id":store.objectId,
                "store_name":store.get('store_name'),
                "subject":feedback.get('subject'),
                "message_id":msg.objectId,
                "filter":'one',
                "username":feedback.get('username'),
            })

            return redirect(reverse('feedback_details', 
                        args=(feedback.objectId,)) +\
                        "?%s" % urllib.urlencode({'success':\
                        'Reply has been sent.'}))
    else:
        data['from_address'] = account.get('username')
        data['subject'] = 'Re: ' + feedback.get('subject')
        
    # update store session cache
    request.session['store'] = store
    
    data['feedback'] = feedback
    
    return render(request, 'manage/feedback_reply.djhtml', data)

@login_required
def feedback_delete(request, feedback_id):
    store = SESSION.get_store(request.session)
    
    feedback = store.get("receivedMessages", objectId=feedback_id)[0]
    # make sure cache attr is None for future queries!
    store.receivedMessages = None
    if not feedback:
        raise Http404

    # delete reply to message first if exist
    if feedback.get('Reply'):
        feedback_reply = feedback.get('reply')
        feedback_reply.delete()
    
    # update messages_received_list in session cache
    messages_received_list = SESSION.get_received_list(\
        request.session)
    i_remove = 0
    for i, m in enumerate(messages_received_list):
        if m.objectId == feedback.objectId:
            i_remove = i
            break
    messages_received_list.pop(i_remove)
    request.session['messages_received_list'] =\
        messages_received_list
    
    # update store session cache
    request.session['store'] = store
    
    feedback.delete()
    return redirect(reverse('messages_index')+ "?%s" % urllib.urlencode({'success': 'Feedback has been deleted.'}))

