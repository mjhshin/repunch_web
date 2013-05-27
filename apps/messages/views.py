from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q
from django.utils import timezone
import urllib, datetime

from apps.messages.models import Message, Feedback
from apps.messages.forms import MessageForm
from libs.repunch import rputils

from django.db import connection
connection.queries

@login_required
def index(request):
    rputils.set_timezone(request)
    data = {'messages_nav': True}
    store = request.session['account'].store
    
    data['messages'] = Message.objects.filter(store=store.id).order_by('-date_added')
    data['feedback'] = Feedback.objects.filter(store=store.id,parent=None).order_by('-date_added')
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/messages.djhtml', data)


@login_required
def edit(request, message_id):
    rputils.set_timezone(request)
    message_id = int(message_id)
    message = None
    account = request.session['account'];
    store = account.store
    data = {'messages_nav': True, 'message_id': message_id}
    data['is_new'] = (message_id==0);
    
    #need to make sure this reward really belongs to this store
    if(message_id > 0):
        try:
            message = Message.objects.filter(store=store).get(id=message_id)
        except Message.DoesNotExist:
            raise Http404
    
    if request.method == 'POST': # If the form has been submitted...
        form = MessageForm(request.POST, instance=message, account=account) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            message = form.save(commit=False)
            message.store = store;
            
            if message.status == 'Sent' and message.date_sent == None:
                message.date_sent = datetime.date.today()
            elif form.data['action']  == 'upgrade' :
                if account.upgrade():
                    message.status = 'Sent'
                    message.date_sent = datetime.date.today()
                    request.session['account'] = account # update with the new subscriptoin
                else:
                    data['error'] = "Error upgrading your account."
            
            
            if not data.has_key('error'):
                message.save();
                
                success_message = "Message has been saved as a draft."
                if message.status == 'Sent':
                    success_message = "Message has been sent."
                
                #reload the store and put it in the session
                if message_id > 0:
                    form = MessageForm(instance=message)
                    data['success'] = success_message
                else:
                    return HttpResponseRedirect(message.get_absolute_url() + "?%s" % urllib.urlencode({'success': success_message}))#Since this is new we need to redirect the page
            else:
                pass #nothing to do for now
        else:
            if 'status' in form.errors:
                data['error'] = form.errors['status']
            else:
                data['error'] = "Unable to save form. Please correct any errors below and submit again."
    else:
        if message_id == 0:
            form = MessageForm()
        else:
            if request.GET.get("error"):
                data['error'] = request.GET.get("error")
            if request.GET.get("success"):
                data['success'] = request.GET.get("success")
            
            form = MessageForm(instance=message)
    
    data['form'] = form

    return render(request, 'manage/message_edit.djhtml', data)

@login_required
def delete(request, message_id):
    message_id = int(message_id)
    message = None
    store = request.session['account'].store
    
    #need to make sure this reward really belongs to this store
    if(message_id > 0):
        try:
            message = Message.objects.filter(store=store.id).get(id=message_id)
        except Message.DoesNotExist:
            raise Http404
    else:
        raise Http404
    
    message.delete()
    return redirect(reverse('messages_index')+ "?%s" % urllib.urlencode({'success': 'Message has been deleted.'}))

@login_required
def duplicate(request, message_id):
    message_id = int(message_id)
    message = None
    store = request.session['account'].store
    
    #need to make sure this reward really belongs to this store
    if(message_id > 0):
        try:
            message = Message.objects.filter(store=store.id).get(id=message_id)
        except Message.DoesNotExist:
            raise Http404
    else:
        raise Http404
    
    #reset values so this is a draft message
    message.pk = None
    message.date_sent = None
    message.status = 'Draft'
    message.save()
    
    return redirect(message.get_absolute_url()+ "?%s" % urllib.urlencode({'success': 'Message has been duplicated.'}))

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

