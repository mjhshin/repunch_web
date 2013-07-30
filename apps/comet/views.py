from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.backends.cache import SessionStore
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.http import HttpResponse
from time import sleep
from dateutil import parser
import json, socket, thread

from libs.dateutil.relativedelta import relativedelta
from parse import session as SESSION
from parse.utils import cloud_call
from parse.auth.decorators import login_required
from apps.comet.models import CometSession, CometSessionIndex
from parse.apps.stores.models import Store, Subscription, Settings
from parse.apps.messages import FEEDBACK
from parse.apps.messages.models import Message
from parse.apps.employees import APPROVED, DENIED
from parse.apps.employees.models import Employee
from parse.apps.rewards.models import RedeemReward
from parse.apps.employees.models import Employee
from repunch.settings import REQUEST_TIMEOUT, COMET_PULL_RATE,\
COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY
   
@login_required
def pull(request):
    """
    This is where the comet approach is put into play.
    This handles ajax requests from clients, holding on to the 
    request while checking Parse for new activity.
    
    IMPORTANT! The order in which the session cache is checked is very
    critical. Take for example and employee that registers.
    Dashboard A receives the pending employee and immediately 
    approves it. Now Dashboard B will run pull with the pending
    employee and the approved employee. We must first add the pending 
    then check for the approved!
    """
    def comet(session_copy):
        # used by more than 1 (note that it is ok to retrieve all of 
        # the lists since they are all pointers - not the actual list!
        employees_pending_list_copy =\
            SESSION.get_employees_pending_list(session_copy)
        employees_approved_list_copy =\
            SESSION.get_employees_approved_list(session_copy)
        messages_received_list_copy =\
            SESSION.get_messages_received_list(session_copy)
        redemptions_pending_copy =\
            SESSION.get_redemptions_pending(session_copy)
        redemptions_past_copy =\
            SESSION.get_redemptions_past(session_copy)
        
        # this is the latest session data
        session = SessionStore(request.session.session_key)
        employees_pending_list =\
            SESSION.get_employees_pending_list(session)
        employees_approved_list =\
            SESSION.get_employees_approved_list(session)
        messages_received_list =\
            SESSION.get_messages_received_list(session)
        redemptions_pending =\
            SESSION.get_redemptions_pending(session)
        redemptions_past =\
            SESSION.get_redemptions_past(session)
        
        # put the diffs between session_copy and session here
        data = {}
        
        #############################################################
        # FEEDBACKS_UNREAD ##################################
        fbs_unread_copy = [ fb.objectId for fb in\
            messages_received_list_copy if not fb.is_read ]
        fbs_unread = [ fb.objectId for fb in\
            messages_received_list if not fb.is_read ]
            
        # get the difference between the two
        feedbacks_unread =\
            tuple(set(fbs_unread) - set(fbs_unread_copy))
        if feedbacks_unread:
            fb_unread = []
            messages_received_ids =\
                [ fb.objectId for fb in messages_received_list ]
            for feedback_id in feedbacks_unread:
                for fb in messages_received_list:
                    if fb.objectId == feedback_id:
                        fb_unread.append(fb.jsonify())
                        break
                
            if len(fb_unread) > 0:
                fb_count = 0
                for fb in messages_received_list:
                    if not fb.get("is_read"):
                        fb_count += 1
                data['feedbacks_unread'] = fb_unread
                data['feedback_unread_count'] = fb_count
          
        #############################################################
        # EMPLOYEES_PENDING ##################################
        # must also check if employee is already approved!
        emps_pending_copy = [ emp.objectId for emp in
            employees_pending_list_copy ]
        emps_pending = [ emp.objectId for emp in
            employees_pending_list ]
            
        employees_pending =\
            tuple(set(emps_pending) - set(emps_pending_copy))
            
        if employees_pending:
            emps_pending = []
            for emp_id in employees_pending:
                for emp in employees_pending_list:
                    if emp.objectId == emp_id:
                        emps_pending.append(emp.jsonify())
                        break
                    
            if len(emps_pending) > 0:   
                data['employees_pending_count'] =\
                    len(employees_pending_list)
                data['employees_pending'] = emps_pending
        
        #############################################################
        # EMPLOYEES APPROVED (pending to approved) #################
        emps_approved_copy = [ emp.objectId for emp in\
            employees_approved_list_copy]
        emps_approved = [ emp.objectId for emp in\
            employees_approved_list]
            
        appr_emps =\
            tuple(set(emps_approved) - set(emps_approved_copy))
        
        if appr_emps:
            emps_approved = []
            for appr_emp_id in appr_emps:
                for emp in employees_approved_list:
                    if emp.objectId == appr_emp_id:
                        emps_approved.append(emp.jsonify())
                        break
                        
            if len(emps_pending) > 0:   
                data['employees_pending_count'] =\
                    len(employees_pending_list)
                data['employees_approved'] = emps_approved
            
        #############################################################
        # EMPLOYEES DELETED/DENIED/REJECTED (pending/approved to pop)!
        # need to compare approved and pending!
        emps_copy = emps_approved_copy[:]
        emps_copy.extend(emps_pending_copy)
        emps = emps_approved[:]
        emps.extend(emps_pending)
        
        # emps_copy has the same or more items that emps
        del_emps = tuple(set(emps_copy) - set(emps))
        
        if del_emps:
            emps_deleted = []
            for demp_id in del_emps:
                if demp_id in emps_approved_copy:
                    emps_list = emps_approved_list_copy
                else:
                    emps_list = emps_pending_list_copy
                    
                for emp in emps_list:
                    if emp.objectId == demp_id:
                        emps_deleted.append(emp.jsonify())
                        break  
                        
            if len(emps_deleted) > 0:   
                data['employees_pending_count'] =\
                    len(employees_pending_list)
                data['employees_deleted'] = emps_deleted
           
        #############################################################
        # REDEMPTIONS PENDING
        reds_pending_copy = [ r.objectId for r in\
            redemptions_pending_copy ]
        reds_pending = [ r.objectId for r in redemptions_pending ]
        
        reds = tuple(set(reds_pending) - set(reds_pending_copy))
        
        if reds:
            redemps = []
            for r_id in reds:
                for redemp in redemptions_pending:
                    if redemp.objectId == r_id:
                        redemps.append(redemp.jsonify())
                        break
                        
            if len(redemps) > 0:
                data['redemption_pending_count'] =\
                    len(redemptions_pending)
                data['redemptions_pending'] = redemps
                
        #############################################################
        # REDEMPTIONS APPROVED (pending to history)
        reds_past_copy = [ r.objectId for r in\
            redemptions_past_copy ]
        reds_past = [ r.objectId for r in redemptions_past ]
        
        appr_redemps =\
            tuple(set(reds_past) - set(reds_past_copy))
            
        if appr_redemps:   
            redemp_js = []
            for red_id in appr_redemps:
                for redemp in redemptions_past:
                    if redemp.objectId == red_id:
                        redemp_js.append(redemp.jsonify())
                        break
            
            if len(redemp_js) > 0:
                data['redemption_pending_count'] =\
                    len(redemptions_pending)
                data['redemptions_approved'] = redemp_js
            
        #############################################################
        # REDEMPTIONS DELETED ##############################
        # remove from pending (should not be in history!)
        reds_copy = reds_past_copy[:]
        reds_copy.extend(reds_pending_copy)
        reds = reds_past[:]
        reds.extend(reds_pending)
        
        # reds_copy has the same or more items that reds
        del_redemps = tuple(set(reds_copy) - set(reds))
        if del_redemps:
            redemp_js = []
            for red_id in del_redemps:
                reds_list = []
                if red_id in reds_past_copy:
                    reds_list = redemptions_past_copy
                elif red_id in reds_pending_copy:
                    reds_list = redemptions_pending_copy
                    
                for redemp in reds_list:
                    if redemp.objectId == red_id:
                        redemp_js.append(redemp.jsonify())
                        break               
            if len(redemp_js) > 0:
                data['redemption_pending_count'] =\
                    len(redemptions_pending)
                data['redemptions_deleted'] = redemp_js
            
        #############################################################
        # SETTINGS UPDATED ##############################
        settings_copy = session_copy.get("settings")
        settings = session.get("settings")
        if settings_copy.get("retailer_pin") !=\
            settings.get("retailer_pin"):
            data['retailer_pin'] = settings.get("retailer_pin")
        
        #############################################################
        # REWARDS UPDATED ##############################
        rewards_copy = session_copy.get("store").get("rewards")
        rewards_copy =\
            { reward['reward_id']:reward for reward in rewards_copy }
            
        rewards = session.get("store").get("rewards")
        rewards = { reward['reward_id']:reward for reward in rewards }
        updated_rewards = []
        
        for reward_id, rew_copy in rewards_copy.iteritems():
            rew = rewards[reward_id]
            if rew_copy['redemption_count']!=rew['redemption_count']:
                # only the redemtpion_count and reward_id are used
                # in the client side
                updated_rewards.append({
                    "reward_id": reward_id,
                    "redemption_count": rew['redemption_count'],
                })
        
        if updated_rewards:
            data['rewards'] = updated_rewards
           
        #############################################################
        # PATRONSTORE_COUNT ##################################
        patronStore_count_copy =int(session_copy["patronStore_count"])
        patronStore_count = int(session["patronStore_count"])
        if patronStore_count_copy != patronStore_count:
            data['patronStore_count'] = patronStore_count

        # IMPORTANT! The request.session is the same as the 
        # SessionStore(session_key)! so we must use the 
        # request.session because it is automatically saved at the end
        # of each request- thereby overriding/undoing any changes made
        # to the SessionStore(session_key) key!
        # need to check if we are still logged in
        session = SessionStore(request.session.session_key)
        if 'account' in session and SESSION_KEY in session:
            request.session.update(session)
        else:
            request.session.flush()
        
        try: # respond
            return HttpResponse(json.dumps(data), 
                        content_type="application/json")
        except (IOError, socket.error) as e: # broken pipe/socket. 
            thread.exit() # exit silently
            
    # get the timestamp and uid
    t = parser.parse(request.GET["timestamp"])
    timestamp = str(t.hour).zfill(2) + ":" +\
        str(t.minute).zfill(2) + ":" + str(t.second).zfill(2)
    uid = request.GET['uid']
    
    # update the last_updated field of the CometSessionIndex
    try:
        csi = CometSessionIndex.objects.get(session_key=\
            request.session.session_key)
        csi.last_updated = timezone.now()
        csi.save()
    except CometSessionIndex.DoesNotExist:
        # should never go here but just in case.
        CometSessionIndex.objects.create(session_key=\
            request.session.session_key, last_updated=timezone.now())
        
        
    # register the comet session
    CometSession.objects.update()
    CometSession.objects.create(session_key=\
        request.session.session_key, timestamp=timestamp, uid=uid, 
        store_id=request.session['store'].objectId)
    
    # cache the current session at this state
    session_copy = dict(request.session)
    timeout_time = timezone.now() + relativedelta(seconds=REQUEST_TIMEOUT)
    
    # keep going until its time to return a response forcibly
    while timezone.now() < timeout_time:  
        # need to update he objects manager to get the latest objects
        CometSession.objects.update() 
        try:     
            scomet = CometSession.objects.get(session_key=\
                request.session.session_key,
                timestamp=timestamp, uid=uid)
        except CometSession.DoesNotExist:
            # cometsession was deleted - time to go
            try:
                # make sure that the latest session is saved!
                # need to check if we are still logged in
                session = SessionStore(request.session.session_key)
                if 'account' in session and SESSION_KEY in session:
                    request.session.update(session)
                else:
                    request.session.flush()
                return HttpResponse(json.dumps({"result":-1}), 
                            content_type="application/json")
            except (IOError, socket.error) as e: 
                thread.exit() 
                
        if scomet.modified:
            # delete the registered comet session object
            CometSession.objects.update()
            try:
                scomet = CometSession.objects.get(session_key=\
                    request.session.session_key,
                    timestamp=timestamp, uid=uid)
                scomet.delete()
            except CometSession.DoesNotExist:
                pass # do nothing
            return comet(session_copy)
        else: # nothing new, sleep for a bit
            sleep(COMET_PULL_RATE)
            
            
    # TIME IS UP - return a response result 0 means no change 
    # try 1 last time
    if scomet.modified:
        # delete the registered comet session object
        CometSession.objects.update()
        try:
            scomet = CometSession.objects.get(session_key=\
                request.session.session_key,
                timestamp=timestamp, uid=uid)
            scomet.delete()
        except CometSession.DoesNotExist:
            pass # do nothing
        return comet(session_copy)
            
    # make sure that request.session is the most up to date
    session = SessionStore(request.session.session_key)
    # need to check if we are still logged in
    if 'account' in session and SESSION_KEY in session:
        request.session.update(session)
    else:
        request.session.flush()
    
    # attempt to delete registered comet session if not yet deleted
    try:
        scomet = CometSession.objects.get(session_key=\
            request.session.session_key,
            timestamp=timestamp, uid=uid)
        scomet.delete()
    except CometSession.DoesNotExist:
        pass # do nothing
    
    try:
        return HttpResponse(json.dumps({"result":0}), 
                        content_type="application/json")
    except (IOError, socket.error) as e:
        thread.exit() # exit silently
        
@login_required
def terminate(request):
    """
    Flags the looping thread in the pull view to exit.
    This simply deletes the CometSession bound to this instance.
    """
    if request.method == "GET" or request.is_ajax():
        t = parser.parse(request.GET["timestamp"])
        timestamp = str(t.hour).zfill(2) + ":" +\
            str(t.minute).zfill(2) + ":" + str(t.second).zfill(2)
        uid = request.GET['uid']
        try:
            scomet = CometSession.objects.get(session_key=\
                request.session.session_key,
                timestamp=timestamp, uid=uid)
            scomet.delete()
        except CometSession.DoesNotExist:
            pass # do nothing
            
        # make sure that the latest session data is saved!
        request.session.update(SessionStore(\
            request.session.session_key))
        
        return HttpResponse("ok")
        
@csrf_exempt  
def receive(request, store_id):
    """
    Receives a get request from a foreign site and sets all of the 
    CometSessions that have the given store Id.
    This is called by a currently logged in user as well as by the
    cloud. Need to differentiate!
    
    IMPORTANT! This should only be called by an anonymous session!
    
    This adds to the related session's cache:
        Note: request.POST does not contain the data!
                Use request.body instead!
    
        updatedStore_one = request.POST.get("updatedStore_one")
        updatedSubscription_one = request.POST.get("updatedStore_one")
        updatedSettings_one = request.POST.get("updatedSettings_one")
        patronStore_num = request.POST.get("patronStore_num")
        newReward = request.POST.get("newReward")
        deletedReward = request.POST.get("deletedReward")
        updatedReward = request.POST.get("updatedReward")
        newMessage = request.POST.get("newMessage")
        newFeedback = request.POST.get("newFeedback")
        deletedFeedback = request.POST.get("deletedFeedback")
        pendingEmployee = request.POST.get("pendingEmployee")
        approvedEmployee = request.POST.get("approvedEmployee")
        deletedEmployee = request.POST.get("deletedEmployee")
        updatedEmployeePunch =request.POST.get("updatedEmployeePunch")
        pendingRedemption = request.POST.get("pendingRedemption")
        approvedRedemption = request.POST.get("approvedRedemption")
        deletedRedemption = request.POST.get("deletedRedemption")
        updatedStoreAvatarName_str
        updatedStoreAvatarUrl_str
        
    Note that since each CometSession is no longer unique to 1 session
    we need to keep track of the session_keys that have already been 
    processed to avoid duplication.     
        
    """
    def processPostDict(session, postDict):
        employees_pending_list =\
            SESSION.get_employees_pending_list(session)
        employees_approved_list =\
            SESSION.get_employees_approved_list(session)
        messages_received_list =\
            SESSION.get_messages_received_list(session)
        redemptions_pending =\
            SESSION.get_redemptions_pending(session)
        redemptions_past =\
            SESSION.get_redemptions_past(session)
        
        #############################################################
        # FEEDBACKS_UNREAD ##################################
        newFeedback = postDict.get('newFeedback')
        if newFeedback:
            messages_received_ids =\
                [ fb.objectId for fb in messages_received_list ]
            m = Message(**newFeedback)
            if m.objectId not in messages_received_ids:
                messages_received_list.insert(0, m)
                
            session['messages_received_list'] =\
                messages_received_list

        #############################################################
        # FEEDBACK DELETED ##################################
        deletedFeedback = postDict.get("deletedFeedback")
        if deletedFeedback:
            fb = Message(**deletedFeedback)
            for i, mro in enumerate(messages_received_list):
                if fb.objectId == mro.objectId:
                    messages_received_list.pop(i)
                    break
            session['messages_received_list'] =\
                messages_received_list
            
            
        #############################################################
        # MESSAGE SENT ##################################
        # need to check if this new message is an original message 
        # or a reply to a feedback (the message sent by the patron)!
        newMessage = postDict.get("newMessage")
        if newMessage:
            messages_received_ids =\
                    [ fb.objectId for fb in messages_received_list ]
            messages_sent_list =\
                SESSION.get_messages_sent_list(session)
            messages_sent_ids =\
                [ msg.objectId for msg in messages_sent_list ]
            m = Message(**newMessage)
            if m.objectId not in messages_sent_ids and\
                m.message_type != FEEDBACK:
                messages_sent_list.insert(0, m)
            # update an existing feedback
            if m.objectId in messages_received_ids and\
                m.message_type == FEEDBACK:
                for i, mrl in enumerate(messages_received_list):
                    if mrl.objectId == m.objectId:
                        messages_received_list.pop(i)
                        messages_received_list.insert(i, m)
                        break
            session['messages_received_list'] =\
                messages_received_list
            session['messages_sent_list'] = messages_sent_list
          
        
        #############################################################
        # EMPLOYEES_PENDING ##################################
        # must also check if employee is already approved!
        pendingEmployee = postDict.get("pendingEmployee")
        if pendingEmployee:
            employees_approved_ids =\
                [ emp.objectId for emp in employees_approved_list ]
            employees_pending_ids =\
                [ emp.objectId for emp in employees_pending_list ]
            e = Employee(**pendingEmployee)
            if e.objectId not in employees_pending_ids and\
                e.objectId not in employees_approved_ids:
                employees_pending_list.insert(0, e)
                
            session['employees_pending_list'] =\
                employees_pending_list
        
        #############################################################
        # EMPLOYEES APPROVED (pending to approved) #################
        approvedEmployee = postDict.get("approvedEmployee")
        if approvedEmployee:
            emp = Employee(**approvedEmployee)
            # first check if the employee is in the pending list
            # if not then check if it is already approved
            for i, emp_pending in\
                enumerate(employees_pending_list):
                if emp.objectId == emp_pending.objectId:
                    emp = employees_pending_list.pop(i)
                    emp.status = APPROVED
                    employees_approved_list.insert(0, emp)
                    break
                
            session['employees_pending_list'] =\
                employees_pending_list
            session['employees_approved_list'] =\
                employees_approved_list
            
        #############################################################
        # EMPLOYEES DELETED/DENIED/REJECTED (pending/approved to pop)!
        deletedEmployee = postDict.get("deletedEmployee")
        if deletedEmployee:
            emp = Employee(**deletedEmployee)
            # check in approved emps
            for i, cop in enumerate(employees_approved_list):
                if cop.objectId == emp.objectId:
                    employees_approved_list.pop(i)
                    break
                
            # check in pending emps
            for i, cop in enumerate(employees_pending_list):
                if cop.objectId == emp.objectId:
                    employees_pending_list.pop(i)
                    break
                        
            session['employees_approved_list'] =\
                employees_approved_list
            session['employees_pending_list'] =\
                employees_pending_list
         
        #############################################################           
        # EMPLOYEE UPDATED PUNCHES
        updatedEmployeePunch = postDict.get("updatedEmployeePunch")
        if updatedEmployeePunch:
            u_emp = Employee(**updatedEmployeePunch)
            for emp in employees_approved_list:
                if u_emp.objectId == emp.objectId:
                    emp.set("lifetime_punches",
                        u_emp.lifetime_punches)
                    break
            session['employees_approved_list'] =\
                employees_approved_list
           
        #############################################################
        # REDEMPTIONS PENDING
        pendingRedemption = postDict.get("pendingRedemption")
        if pendingRedemption:
            redemptions_pending_ids =\
                [ red.objectId for red in redemptions_pending ]
            redemptions_past_ids =\
                [ red.objectId for red in redemptions_past ]
            rr = RedeemReward(**pendingRedemption)
            # need to check here if the redemption is new because 
            # the dashboard that validated it will also receive
            # the validated redemption back.
            if rr.objectId not in redemptions_past_ids and\
                rr.objectId not in redemptions_pending_ids:
                redemptions_pending.insert(0, rr)
                
            session['redemptions_pending'] =\
                redemptions_pending
            
        #############################################################
        # REDEMPTIONS APPROVED (pending to history)
        approvedRedemption = postDict.get("approvedRedemption") 
        if approvedRedemption:  
            redemp = RedeemReward(**approvedRedemption)
            # check if redemp is still in pending
            for i, redem in enumerate(redemptions_pending):
                if redem.objectId == redemp.objectId:
                    r = redemptions_pending.pop(i)
                    r.is_redeemed = True
                    redemptions_past.insert(0, r)
                    break
            # if not then check if it is in the history already
            # the above shouldn't happen!
                
            session['redemptions_pending'] =\
                redemptions_pending
            session['redemptions_past'] =\
                redemptions_past
            
        #############################################################
        # REDEMPTIONS DELETED ##############################
        # remove from pending (should not be in history!)
        deletedRedemption = postDict.get("deletedRedemption")
        if deletedRedemption:
            redemp = RedeemReward(**deletedRedemption)
            # check if redemp is still in pending
            for i, redem in enumerate(redemptions_pending):
                if redem.objectId == redemp.objectId:
                    redemptions_pending.pop(i)
                    break
                
            session['redemptions_pending'] =\
                redemptions_pending
               
        #############################################################
        # STORE UPDATED ##############################
        updatedStore_one = postDict.get("updatedStore_one")
        if updatedStore_one:
            session['store'] = Store(**updatedStore_one)
            
        updatedStoreAvatarName_str =\
            postDict.get("updatedStoreAvatarName_str")
        if updatedStoreAvatarName_str:
            store = session['store']
            updatedStoreAvatarUrl_str =\
                postDict.get("updatedStoreAvatarUrl_str")
            if updatedStoreAvatarUrl_str:
                store.store_avatar_url = updatedStoreAvatarUrl_str
            store.store_avatar = updatedStoreAvatarName_str            
            
        #############################################################
        # SUBSCRIPTION UPDATED ##############################
        updatedSubscription_one =\
            postDict.get("updatedSubscription_one")
        if updatedSubscription_one:
            subscription = Subscription(**updatedSubscription_one)
            store = session["store"]
            store.set('subscription', subscription)
            store.set('Subscription', subscription.objectId)
            session['subscription'] = subscription
            session['store'] = store
            
        #############################################################
        # SETTINGS UPDATED ##############################
        updatedSettings_one = postDict.get("updatedSettings_one")
        if updatedSettings_one:
            settings = Settings(**updatedSettings_one)
            store = session["store"]
            store.set('settings', settings)
            store.set("Settings", settings.objectId)
            session['settings'] = settings
            session['store'] = store
            
        #############################################################
        # REWARDS NEW ##############################
        newReward = postDict.get("newReward")
        if newReward:
            store = session['store']
            rewards = store.get("rewards")
            rewards_ids = [ r['reward_id'] for r in rewards ]
            if newReward['reward_id'] not in rewards_ids:
                rewards.append(reward)
            store.rewards = rewards
            session['store'] = store
        
        #############################################################
        # REWARDS UPDATED ##############################
        updatedReward = postDict.get('updatedReward')
        if updatedReward:
            store = session['store']
            mod_rewards = store.get("rewards")
            for i, mreward in enumerate(mod_rewards):
                # [{"reward_name":"Free bottle of wine", 
                # "description":"Must be under $25 in value",
                # "punches":10,"redemption_count":0,reward_id:0},]
                if updatedReward['reward_id']==mreward['reward_id']:
                    if updatedReward.has_key("redemption_count"):
                        mod_rewards[i]['redemption_count'] =\
                            updatedReward['redemption_count']
                    if updatedReward.has_key("reward_name"):
                        mod_rewards[i]['reward_name'] =\
                            updatedReward['reward_name']
                    if updatedReward.has_key("punches"):
                        mod_rewards[i]['punches'] =\
                            updatedReward['punches']
                    if updatedReward.has_key("description"):
                        mod_rewards[i]['description'] =\
                            updatedReward['description']
                    break
                        
            store.rewards = mod_rewards
            session['store'] = store
            
        #############################################################
        # REWARDS DELETED ##############################
        deletedReward = postDict.get("deletedReward")
        if deletedReward:
            store = session['store']
            rewards = store.get("rewards")
            rewards_ids = [ r['reward_id'] for r in rewards ]
            if deletedReward['reward_id'] in rewards_ids:
                for i, r in enumerate(rewards):
                    if r['reward_id'] == deletedReward['reward_id']:
                        rewards.pop(i)
                        break
            store.rewards = rewards
            session['store'] = store
           
        #############################################################
        # PATRONSTORE_COUNT ##################################
        patronStore_num = postDict.get('patronStore_num')
        if patronStore_num:
            patronStore_num = int(patronStore_num)
            session['patronStore_count'] = patronStore_num
    
    
    # ENTRY POINT
    if request.method == "POST" or request.is_ajax():
        postDict = json.loads(request.body)
        
        # check if key is present and valid
        if postDict.get(COMET_RECEIVE_KEY_NAME) != COMET_RECEIVE_KEY:
            return HttpResponse("error")
            
        for scomet in CometSessionIndex.objects.filter(\
            store_id=store_id):
            # flag all threads with this session_key that new stuff
            scomet.modified = True
            scomet.save() 
            
            # get the latest session associated with this object
            session = SessionStore(scomet.session_key)
            # do not go if the session has already been logged out
            if session.get('account') is None or\
                SESSION_KEY not in session:
                continue
            processPostDict(session, postDict)
                        
            # need to save session to commit modifications
            session.modified = True
            session.save()
            
        return HttpResponse("success")
        
    return HttpResponse("error")
    
    
    
    
    
    
    
    
    
    
    








