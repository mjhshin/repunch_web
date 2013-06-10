from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q
from django.utils import timezone
from dateutil import parser
import urllib, datetime

from parse.auth.decorators import login_required
from parse.apps.messages.models import Message
from parse.apps.messages import RETAILER, FILTERS
from apps.messages.forms import MessageForm
from libs.repunch import rputils

from django.db import connection
connection.queries

@login_required
def index(request):
    rputils.set_timezone(request)
    data = {'messages_nav': True}
    store = request.session['account'].get('store')
        
    data['messages'] = store.get("sentMessages")
    data['feedback'] = store.get("receivedMessages")
    
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
            message = Message.objects().create(message_type=\
                RETAILER, store_id=store.objectId)
            message.update_locally(request.POST.dict(), False)

            # check if attach offer is selected
            if 'attach_offer' in request.POST.dict():
                # make sure that date is a date and not string
                message.set('date_offer_expiration', 
                    parser.parse(request.POST['attach_offer']) )
            else:
                # pop the offer
                message.set('offer_title', None)
                message.set('date_offer_expiration', None)

            message.update()
            data['message'] = message
            # add to the store's relation
            store.add_relation("SentMessages_", [message.objectId]) 
            # update the session
            account.set('store', store)
            request.session['account'] = account
            success_message = "Message has been sent."

            # call cloud function TODO

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
            
            message = store.get("sentMessages", objectId=message_id)[0]
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
    store = request.session['account'].store
    
    message = store.get("sentMessages", objectId=message_id)[0]
    if not message:
        raise Http404

    # delete reply to message first if exist
    if message.get('Reply'):
        msg_reply = message.get('reply')
        msg_reply.delete()
    
    message.delete()
    return redirect(reverse('messages_index')+\
            "?%s" % urllib.urlencode({'success':\
            'Message has been deleted.'}))

# FEEDBACK ------------------------------------------
@login_required
def feedback(request, feedback_id):
    feedback_id = int(feedback_id)
    feedback = None
    account = request.session['account']
    store = account.store
    data = {'messages_nav': True, 'feedback_id': feedback_id, 'account_username': account.username}    
    
    #need to make sure this reward really belongs to this store
    if(feedback_id > 0):
        try:
            feedback = Feedback.objects.filter(store=store.id).get(id=feedback_id)            
        except Feedback.DoesNotExist:
            raise Http404
    else:
        raise Http404
    
    if feedback.status == 0:
        feedback.status = 1
        feedback.save()
        
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    replies = Feedback.objects.filter(Q(parent_id=feedback.id) | Q(id=feedback_id)).order_by('-date_added');
    data['replies'] = replies
    
    # if there are more than on message from client for this thread
    # we need to find the most recent and show that
    if replies != None and len(replies) > 1:
        for reply in replies:
            if reply.is_response == 0:
                feedback = reply
                break

    data['feedback'] = feedback
    
    return render(request, 'manage/feedback.djhtml', data)

@login_required
def feedback_reply(request, feedback_id):
    feedback_id = int(feedback_id)
    feedback = None
    account = request.session['account']
    store = account.store
    data = {'messages_nav': True}    
    
    #need to make sure this reward really belongs to this store
    if(feedback_id > 0):
        try:
            feedback = Feedback.objects.filter(store=store).get(id=feedback_id)            
        except Feedback.DoesNotExist:
            raise Http404
    else:
        raise Http404
    
    if request.method == 'POST':
        message = request.POST.get('message')
        if message == None or len(message) == 0:
            data['error'] = 'Please enter a message.'
        else:
            subject = feedback.subject
            if subject.startswith("Re: ") == False:
                subject = 'Re: ' + subject
                
            parent = feedback
            if feedback.parent != None:
                parent = feedback.parent
                
            reply = Feedback(
                             store=store, 
                             parent=parent, 
                             is_response=1, 
                             patron=feedback.patron, 
                             subject=subject,
                             message=message,
                             status=1)
            reply.save();
            return redirect(feedback.get_absolute_url() + "?%s" % urllib.urlencode({'success': 'Reply has been sent.'}))
    else:
        data['from_address'] = account.username
        
        subject = feedback.subject
        if subject.startswith("Re: ") == False:
            subject = 'Re: ' + subject
        data['subject'] = subject
    
    data['feedback'] = feedback
    
    return render(request, 'manage/feedback_reply.djhtml', data)

@login_required
def feedback_delete(request, feedback_id):
    feedback_id = int(feedback_id)
    feedback = None
    store = request.session['account'].store
    
    #need to make sure this reward really belongs to this store
    if(feedback_id > 0):
        try:
            feedback = Feedback.objects.filter(store=store.id).get(id=feedback_id)
        except Feedback.DoesNotExist:
            raise Http404
    else:
        raise Http404
    
    feedback.delete()
    return redirect(reverse('messages_index')+ "?%s" % urllib.urlencode({'success': 'Feedback has been deleted.'}))

