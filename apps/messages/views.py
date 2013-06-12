from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q
from django.utils import timezone
from dateutil import parser
import urllib, datetime

from parse.utils import cloud_call
from parse.auth.decorators import login_required
from parse.apps.messages.models import Message
from parse.apps.messages import BASIC, OFFER, FEEDBACK, FILTERS
from apps.messages.forms import MessageForm
from libs.repunch import rputils
from libs.dateutil.relativedelta import relativedelta

from django.db import connection
connection.queries

@login_required
def index(request):
    rputils.set_timezone(request)
    data = {'messages_nav': True}
    store = request.session['account'].get('store')
        
    data['messages'] = store.get("sentMessages")
    # when a store replies, it also gets stored in the received
    # with message type BASIC or OFFER
    data['feedback'] = store.get("receivedMessages", 
                            message_type=FEEDBACK)
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/messages.djhtml', data)


@login_required
def edit(request, message_id):
    rputils.set_timezone(request)
    account = request.session['account']
    store = account.get('store')

    data = {'messages_nav': True, 'message_id': message_id,
        "filters": FILTERS}
    
    if request.method == 'POST':
        form = MessageForm(request.POST) 
        # check here if limit has been reached TODO
        limit_reached = False
        data['limit_reached'] = limit_reached

        if form.is_valid() and not limit_reached:
            if form.data.get('action')  == 'upgrade':
                # TODO upgrade
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
                # make sure that date is a date and not string
                message.set('date_offer_expiration', 
                    parser.parse(request.POST['attach_offer']) )
                message.set('message_type', OFFER)
            else:
                # pop the offer
                message.set('offer_title', None)
                message.set('date_offer_expiration', None)
                message.set('message_type', BASIC)

            message.update()
            data['message'] = message
            # add to the store's relation
            store.add_relation("SentMessages_", [message.objectId]) 
            # update the session
            account.set('store', store)
            request.session['account'] = account
            success_message = "Message has been sent."

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
                params.update({idle_date:d.isoformat()})
            elif msg_filter == "most_loyal":
                params.update({min_punches:\
                    request.POST['min_punches']})

            # push notification
            print cloud_call("retailer_message", params)

            return HttpResponseRedirect(message.get_absolute_url())

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
            
            message = store.get("sentMessages", 
                    objectId=message_id)[0]
            data['message'] = message
            form = MessageForm(message.__dict__)
    
    data['form'] = form

    return render(request, 'manage/message_edit.djhtml', data)

@login_required
def details(request, message_id):
    store = request.session['account'].get('store')

    message = store.get("sentMessages", objectId=message_id)[0]
    if not message:
        raise Http404

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
    store = account.store
    data = {'messages_nav': True, 'feedback_id':\
            feedback_id, 'account_username':\
            account.get('username')}    
    
    feedback = store.get("receivedMessages", objectId=feedback_id)[0]
    if not feedback:
        raise Http404
    
    if not feedback.is_read:
        feedback.is_read = True
        feedback.update()
        
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    # there should only be at most 1 reply
    data['reply'] = feedback.get('reply')
    data['feedback'] = feedback
    
    return render(request, 'manage/feedback.djhtml', data)

@login_required
def feedback_reply(request, feedback_id):
    account = request.session['account']
    store = account.store
    data = {'messages_nav': True}    
    
    feedback = store.get("receivedMessages", objectId=feedback_id)[0]
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
            # create BASIC message
            msg = Message.objects().create(message_type=\
                BASIC, sender_name=store.get('store_name'),
                store_id=store.objectId, body=body)
            # add to ReceivedMessages relation
            store.add_relation("ReceivedMessages_", [msg.objectId])
            # set feedback Reply pointer to message
            feedback.set('Reply', msg.objectId)
            feedback.update()

            # push notification
            print cloud_call("retailer_message", {
                "store_id":store.objectId,
                "store_name":store.get('store_name'),
                "subject":message.get('subject'),
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
    
    data['feedback'] = feedback
    
    return render(request, 'manage/feedback_reply.djhtml', data)

@login_required
def feedback_delete(request, feedback_id):
    store = request.session['account'].store
    
    feedback = store.get("receivedMessages", objectId=feedback_id)[0]
    if not feedback:
        raise Http404

    # delete reply to message first if exist
    if feedback.get('Reply'):
        feedback_reply = feedback.get('reply')
        feedback_reply.delete()
    
    feedback.delete()
    return redirect(reverse('messages_index')+ "?%s" % urllib.urlencode({'success': 'Feedback has been deleted.'}))

