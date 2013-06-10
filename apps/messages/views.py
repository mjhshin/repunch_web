from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q
from django.utils import timezone
import urllib, datetime

from parse.auth.decorators import login_required
from parse.apps.messages.models import Message
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
    print data['messages']
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
    
    is_new = message_id == 0 
    data = {'messages_nav': True, 'message_id': message_id,
            'is_new':is_new}
    
    if not is_new: # retrieve the message
        message = store.get("sentMessages", objectId=message_id)[0]
        if not message:
            raise Http404
    else: # create the message
        message = Message.objects().create(message_type=\
                Message.RETAILER, store_id=store.objectId)
    
    if request.method == 'POST':
        form = MessageForm(request.POST) 
        if form.is_valid():
            if form.data['action']  == 'upgrade':
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
            
            message.update_locally(request.POST.dict())
            message.update()
            # call cloud function TODO
            success_message = "Message has been sent."
            if not is_new:
                form = MessageForm(message.__dict__)
                data['success'] = success_message
            else:
                return HttpResponseRedirect(message.get_absolute_url() + "?%s" % urllib.urlencode({'success': success_message}))

        else:
            data['error'] = "The form you submitted has errors."
    else:
        if message_id == 0:
            form = MessageForm()
        else:
            if request.GET.get("error"):
                data['error'] = request.GET.get("error")
            if request.GET.get("success"):
                data['success'] = request.GET.get("success")
            
            form = MessageForm(message.__dict__)
    
    data['form'] = form
    data['message'] = message

    return render(request, 'manage/message_edit.djhtml', data)

@login_required
def delete(request, message_id):
    store = request.session['account'].store
    
    message = store.get("sentMessages", objectId=message_id)[0]
    if not message:
        raise Http404
    
    message.delete()
    return redirect(reverse('messages_index')+\
            "?%s" % urllib.urlencode({'success':\
            'Message has been deleted.'}))

@login_required
def duplicate(request, message_id):
    """ this is a resend feature so that stores do not have to type
    the same message again to send it to the same group """
    
    store = request.session['account'].get('store')
    
    message = store.get("sentMessages", objectId=message_id)[0]
    if not message:
        raise Http404
    
    # make a copy of the message but do not create it up to parse!
    dup_message = Message(message_type=\
                Message.RETAILER, store_id=store.objectId,
                subject=dup_message.get('subject'), 
                body=dup_message.get('body'),
                offer_title=dup_message.get('offer_title'),
                date_offer_expiration=\
                    dup_message.get('date_offer_expiration') )
    
    return redirect(dup_message.get_absolute_url()+ "?%s" % urllib.urlencode({'success': 'Message has been duplicated.'}))

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

