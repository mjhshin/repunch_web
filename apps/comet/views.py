from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.backends.cache import SessionStore
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
import json

from parse import session as SESSION
from parse.utils import cloud_call
from parse.auth.decorators import login_required
from apps.comet.models import CometSession
from parse.apps.messages.models import Message
from parse.apps.employees.models import Employee
from parse.apps.rewards.models import RedeemReward
from repunch.settings import REQUEST_TIMEOUT, COMET_REFRESH_RATE
   
@login_required
def refresh(request):
    """
    This is where the comet approach is put into play.
    This handles ajax requests from clients, holding on to the 
    request while checking Parse for new activity.
    """
    # in_time = timezone.now()
    # out_time = in_time + relativedelta(seconds=REQUEST_TIMEOUT)
    def comet(session_key):
        # sleep(COMET_REFRESH_RATE)
        # prep the params
        store = SESSION.get_store(request.session)
        redemptions_pending =\
            SESSION.get_redemptions_pending(request.session)
        redemptions_past =\
            SESSION.get_redemptions_past(request.session)
        messages_received_list =\
            SESSION.get_messages_received_list(request.session)
        employees_pending_list =\
            SESSION.get_employees_pending_list(request.session)
        employees_approved_list =\
            SESSION.get_employees_approved_list(request.session)
            
        # get the session
        session = SessionStore(scomet.session_key)
        
        # process the stuff in the session
        data = {}
        # rewards redemption_count
        rewards = session.get('updatedReward')
        mod_rewards = store.get('rewards')
        if rewards:
            for reward in rewards:
                for i, mreward in enumerate(mod_rewards):
                    if reward['reward_id']==mreward['reward_id']:
                        mod_rewards[i]['redemption_count'] =\
                            reward['redemption_count']
                        break
            data['rewards'] = rewards
            store.rewards = mod_rewards
            request.session['store'] = store
            del session['updatedReward']
            
        # patronStore_count
        patronStore_count_new = session.get('patronStore_num')
        if patronStore_count_new:
            # TODO patronStore_num > store limit then upgrade account
            # and send email notification make sure to update the
            # subscription in the cache afterwards!
            data['patronStore_count'] = patronStore_count_new
            request.session['patronStore_count']=patronStore_count_new
            del session['patronStore_num']
            
        # feedbacks_unread
        feedbacks_unread = session.get('newFeedback')
        if feedbacks_unread:
            data['feedbacks_unread'] = []
            for feedback in feedbacks_unread:
                m = Message(**feedback)
                messages_received_list.insert(0, m)
                data['feedbacks_unread'].append(m.jsonify())
            request.session['messages_received_list'] =\
                messages_received_list
            fb_count = 0
            for fb in messages_received_list:
                if not fb.get("is_read"):
                    fb_count += 1
            data['feedback_unread_count'] = fb_count
            del session['newFeedback']
            
        # employees_pending
        employees_pending = session.get("pendingEmployee")
        if employees_pending:
            data['employees_pending'] = []
            for emp in employees_pending:
                e = Employee(**emp)
                employees_pending_list.insert(0, e)
                data['employees_pending'].append(e.jsonify())
            request.session['employees_pending_list'] =\
                employees_pending_list
            data['employees_pending_count'] = len(employees_pending_list)
            del session['pendingEmployee']
            
        """
        + patronStore_num = request.POST.get("patronStore_num")
        + employeeLPunches_num =\
            request.POST.get("employeeLPunches_num")
        + updatedReward = request.POST.get("updatedReward")
        newMessage = request.POST.get("newMessage")
        + newFeedback = request.POST.get("newFeedback")
        + pendingEmployee = request.POST.get("pendingEmployee")
        approvedEmployee = request.POST.get("approvedEmployee")
        deletedEmployee = request.POST.get("deletedEmployee")
        + pendingRedemption = request.POST.get("pendingRedemption")
        approvedRedemption = request.POST.get("approvedRedemption")
        deletedRedemption = request.POST.get("deletedRedemption")
        """
            
        # redemptions
        reds, redemps = session.get("pendingRedemption"), []
        redemptions_pending_ids =\
            [ red.objectId for red in redemptions_pending]
        redemptions_past_ids =\
            [ red.objectId for red in redemptions_past]
        if reds:
            for r in reds:
                rr = RedeemReward(**r)
                if rr.objectId not in redemptions_past_ids or\
                    rr.objectId not in redemptions_pending_ids:
                    redemptions_pending.insert(0, rr)
                    request.session['redemptions_pending'] =\
                        redemptions_pending
                    redemps.append(rr.jsonify())
            data['redemption_pending_count'] =\
                len(redemptions_pending)
            data['redemptions_pending'] = redemps
            del session['pendingRedemption']
        
        # make sure to update the session!
        session.save()
        
        # respond
        try:
            resp = HttpResponse(json.dumps(data), 
                        content_type="application/json")
            return resp
        except IOError: # broken pipe or something. 
            # exit silently
            thread.exit()
    
    # the above is different from SESSION_KEY (which is not unique)
    try: # attempt to get a used CometSession first
        scomet = CometSession.objects.get(session_key=\
            request.session.session_key)
        if scomet.modified:
            scomet.modified = False
            scomet.save()
            return comet(scomet.session_key)
            
        return HttpResponse(json.dumps({"result":0}), 
                        content_type="application/json")
    except CometSession.DoesNotExist:
        # this should have been created at login!
        scomet = CometSession.objects.create(session_key=\
                request.session.session_key,
                store_id=SESSION.get_store(request.session).objectId)
        return comet(scomet.session_key)
        
@csrf_exempt  
def receive(request, store_id):
    """
    Receives a get request from a foreign site and sets all of the 
    CometSessions that have the given store Id.
    
    This adds to the related session's cache:
    
        + patronStore_num = request.POST.get("patronStore_num")
        + employeeLPunches_num =\
            request.POST.get("employeeLPunches_num")
        + updatedReward = request.POST.get("updatedReward")
        + newMessage = request.POST.get("newMessage")
        + newFeedback = request.POST.get("newFeedback")
        pendingEmployee = request.POST.get("pendingEmployee")
        approvedEmployee = request.POST.get("approvedEmployee")
        deletedEmployee = request.POST.get("deletedEmployee")
        + pendingRedemption = request.POST.get("pendingRedemption")
        approvedRedemption = request.POST.get("approvedRedemption")
        deletedRedemption = request.POST.get("deletedRedemption")
        
    """
    if request.method == "POST" or request.is_ajax():
        # employeeLPunches_num : updated employee LP count
        # patronStoreCount : amount of new patrons
        # reward : updated reward object
        # message : new message object (from store or patron)
        # employees : pending/approved/deleted employee object
        # redemptions : pending/approved/deleted RedeemReward object
        
        postDict = json.loads(request.raw_post_data)
        for scomet in CometSession.objects.filter(store_id=store_id):
            session = SessionStore(scomet.session_key)
            for key, value in postDict.iteritems():
                if key not in session:
                    # keys ending with _num is a number
                    if key.endswith("_num") or key.endswith("_count"):
                        session[key] = value
                    # everything else is a list of dicts
                    else:
                        session[key] = [value]
                else:
                    # keys ending with _num is a number
                    if key.endswith("_num"):
                        session[key] = session[key]
                    # keys ending in _count is a number that is added
                    elif key.endswith("_count"):
                        session[key] = session[key] + value
                    # everything else is a list of dicts
                    else:
                        session[key].append(value)
                        
            # need to save session to commit modifications
            session.save()
            
            # done additions - set to modified
            scomet.modified = True
            scomet.save()
            
        return HttpResponse("success")
    return HttpResponse("error")
    
    
    
    
    
    
    
    
    
    
    








