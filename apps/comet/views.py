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
from apps.comet.models import CometSession
from parse.apps.stores.models import Store, Subscription, Settings
from parse.apps.messages import FEEDBACK
from parse.apps.messages.models import Message
from parse.apps.employees import APPROVED, DENIED
from parse.apps.employees.models import Employee
from parse.apps.rewards.models import RedeemReward
from parse.apps.employees.models import Employee
from repunch.settings import REQUEST_TIMEOUT, COMET_REFRESH_RATE
   
@login_required
def refresh(request):
    """
    This is where the comet approach is put into play.
    This handles ajax requests from clients, holding on to the 
    request while checking Parse for new activity.
    
    IMPORTANT! The order in which the session cache is checked is very
    critical. Take for example and employee that registers.
    Dashboard A receives the pending employee and immediately 
    approves it. Now Dashboard B will run refresh with the pending
    employee and the approved employee. We must first add the pending 
    then check for the approved!
    """
    def comet(session):
        # used by more than 1 (note that it is ok to retrieve all of 
        # the lists since they are all pointers - not the actual list!
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
        
        # process the stuff in the session
        data = {}
       
        #############################################################
        # FEEDBACKS_UNREAD ##################################
        feedbacks_unread = session.get('newFeedback')
        if feedbacks_unread:
            fb_unread = []
            messages_received_ids =\
                [ fb.objectId for fb in messages_received_list ]
            for feedback in feedbacks_unread:
                m = Message(**feedback)
                if m.objectId not in messages_received_ids:
                    messages_received_list.insert(0, m)
                    fb_unread.append(m.jsonify())
                
            if len(fb_unread) > 0:
                fb_count = 0
                for fb in messages_received_list:
                    if not fb.get("is_read"):
                        fb_count += 1
                data['feedbacks_unread'] = fb_unread
                data['feedback_unread_count'] = fb_count
                
            session['messages_received_list'] =\
                messages_received_list
            session['newFeedback'] = None

        #############################################################
        # FEEDBACK DELETED ##################################
        feedbacks_deleted = session.get("deletedFeedback")
        if feedbacks_deleted:
            for fb_d in feedbacks_deleted:
                fb = Message(**fb_d)
                for i, mro in enumerate(messages_received_list):
                    if fb.objectId == mro.objectId:
                        messages_received_list.pop(i)
                        break
            session['messages_received_list'] =\
                messages_received_list
            session['deletedFeedback'] = None
            
            
        #############################################################
        # MESSAGE SENT ##################################
        # need to check if this new message is an original message 
        # or a reply to a feedback (the message sent by the patron)!
        messages_sent = session.get("newMessage")
        if messages_sent:
            messages_received_ids =\
                    [ fb.objectId for fb in messages_received_list ]
            messages_sent_list =\
                SESSION.get_messages_sent_list(session)
            messages_sent_ids =\
                [ msg.objectId for msg in messages_sent_list ]
            for message in messages_sent:
                m = Message(**message)
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
            session['newMessage'] = None
          
        
        #############################################################
        # EMPLOYEES_PENDING ##################################
        # must also check if employee is already approved!
        employees_pending = session.get("pendingEmployee")
        if employees_pending:
            emps_pending = []
            employees_approved_ids =\
                [ emp.objectId for emp in employees_approved_list ]
            employees_pending_ids =\
                [ emp.objectId for emp in employees_pending_list ]
            for emp in employees_pending:
                e = Employee(**emp)
                if e.objectId not in employees_pending_ids and\
                    e.objectId not in employees_approved_ids:
                    employees_pending_list.insert(0, e)
                    emps_pending.append(e.jsonify())
                    
            if len(emps_pending) > 0:   
                data['employees_pending_count'] =\
                    len(employees_pending_list)
                data['employees_pending'] = emps_pending
                
            session['employees_pending_list'] =\
                employees_pending_list
            session['pendingEmployee'] = None
        
        #############################################################
        # EMPLOYEES APPROVED (pending to approved) #################
        appr_emps = session.get("approvedEmployee")
        if appr_emps:
            emps_approved = []
            for appr_emp in appr_emps:
                emp = Employee(**appr_emp)
                # first check if the employee is in the pending list
                # if not then check if it is already approved
                for i, emp_pending in\
                    enumerate(employees_pending_list):
                    if emp.objectId == emp_pending.objectId:
                        emp = employees_pending_list.pop(i)
                        emp.status = APPROVED
                        emps_approved.append(emp.jsonify())
                        employees_approved_list.insert(0, emp)
                        break
                        
            if len(emps_pending) > 0:   
                data['employees_pending_count'] =\
                    len(employees_pending_list)
                data['employees_approved'] = emps_approved
                
            session['employees_pending_list'] =\
                employees_pending_list
            session['employees_approved_list'] =\
                employees_approved_list
            session['approvedEmployee'] = None
            
        #############################################################
        # EMPLOYEES DELETED/DENIED/REJECTED (pending/approved to pop)!
        del_emps = session.get("deletedEmployee")
        if del_emps:
            emps_deleted = []
            for demp in del_emps:
                emp = Employee(**demp)
                cont = True
                # check in approved emps
                for i, cop in enumerate(employees_approved_list):
                    if cop.objectId == emp.objectId:
                        employees_approved_list.pop(i)
                        emps_deleted.append(emp.jsonify())
                        cont = False
                        break
                    
                if not cont:
                    break
                    
                # check in pending emps
                for i, cop in enumerate(employees_pending_list):
                    if cop.objectId == emp.objectId:
                        employees_pending_list.pop(i)
                        emps_deleted.append(emp.jsonify())
                        break
                        
            if len(emps_deleted) > 0:   
                data['employees_pending_count'] =\
                    len(employees_pending_list)
                data['employees_deleted'] = emps_deleted
                        
            session['employees_approved_list'] =\
                employees_approved_list
            session['employees_pending_list'] =\
                employees_pending_list
            session['deletedEmployee'] = None
         
        #############################################################           
        # EMPLOYEE UPDATED PUNCHES
        uep = session.get("updatedEmployeePunch")
        if uep:
            for updated_emp in uep:
                u_emp = Employee(**updated_emp)
                for emp in employees_approved_list:
                    if u_emp.objectId == emp.objectId:
                        emp.set("lifetime_punches",
                            u_emp.lifetime_punches)
                        break
            session['updatedEmployeePunch'] = None
           
        #############################################################
        # REDEMPTIONS PENDING
        reds = session.get("pendingRedemption")
        if reds:
            redemptions_pending_ids =\
                [ red.objectId for red in redemptions_pending ]
            redemptions_past_ids =\
                [ red.objectId for red in redemptions_past ]
            redemps = []
            for r in reds:
                rr = RedeemReward(**r)
                # need to check here if the redemption is new because 
                # the dashboard that validated it will also receive
                # the validated redemption back.
                if rr.objectId not in redemptions_past_ids and\
                    rr.objectId not in redemptions_pending_ids:
                    redemptions_pending.insert(0, rr)
                    redemps.append(rr.jsonify())
            if len(redemps) > 0:
                data['redemption_pending_count'] =\
                    len(redemptions_pending)
                data['redemptions_pending'] = redemps
                
            session['redemptions_pending'] =\
                redemptions_pending
            session['pendingRedemption'] = None
            
        #############################################################
        # REDEMPTIONS APPROVED (pending to history)
        appr_redemps = session.get("approvedRedemption") 
        if appr_redemps:   
            redemp_js = []
            for red in appr_redemps:
                redemp = RedeemReward(**red)
                # check if redemp is still in pending
                for i, redem in enumerate(redemptions_pending):
                    if redem.objectId == redemp.objectId:
                        r = redemptions_pending.pop(i)
                        r.is_redeemed = True
                        redemptions_past.insert(0, r)
                        redemp_js.append(r.jsonify())
                        break
                # if not then check if it is in the history already
                # the above shouldn't happen!
            if len(redemp_js) > 0:
                data['redemption_pending_count'] =\
                    len(redemptions_pending)
                data['redemptions_approved'] = redemp_js
                
            session['redemptions_pending'] =\
                redemptions_pending
            session['redemptions_past'] =\
                redemptions_past
            session['approvedRedemption'] = None
            
        #############################################################
        # REDEMPTIONS DELETED ##############################
        # remove from pending (should not be in history!)
        del_redemps = session.get("deletedRedemption")
        if del_redemps:
            redemp_js = []
            for red in del_redemps:
                redemp = RedeemReward(**red)
                # check if redemp is still in pending
                for i, redem in enumerate(redemptions_pending):
                    if redem.objectId == redemp.objectId:
                        redemp_js.append(\
                            redemptions_pending.pop(i).jsonify())
                        break
                
            if len(redemp_js) > 0:
                data['redemptions_deleted'] = redemp_js
                
            session['redemptions_pending'] =\
                redemptions_pending
            session['deletedRedemption'] = None
               
        #############################################################
        # STORE UPDATED ##############################
        updatedStore = session.get("updatedStore_one")
        if updatedStore:
            session['store'] = Store(**updatedStore)
            session["updatedStore_one"] = None
            
        #############################################################
        # SUBSCRIPTION UPDATED ##############################
        updatedSubscription = session.get("updatedSubscription_one")
        if updatedSubscription:
            subscription = Subscription(**updatedSubscription)
            store = session["store"]
            store.set('subscription', subscription)
            store.set('Subscription', subscription.objectId)
            session['subscription'] = subscription
            session['store'] = store
            session["updatedSubscription_one"] = None
            
        #############################################################
        # SETTINGS UPDATED ##############################
        updatedSettings = session.get("updatedSettings_one")
        if updatedSettings:
            settings = Settings(**updatedSettings)
            store = session["store"]
            store.set('settings', settings)
            store.set("Settings", settings.objectId)
            session['settings'] = settings
            session['store'] = store
            data['retailer_pin'] = settings.get("retailer_pin")
            session["updatedSettings_one"] = None
            
        #############################################################
        # REWARDS NEW ##############################
        new_rewards = session.get("newReward")
        if new_rewards:
            store = session['store']
            rewards = store.get("rewards")
            rewards_ids = [ r['reward_id'] for r in rewards ]
            for reward in new_rewards:
                if reward['reward_id'] not in rewards_ids:
                    rewards.append(reward)
            store.rewards = rewards
            session['store'] = store
            session['newReward'] = None
        
        #############################################################
        # REWARDS UPDATED ##############################
        updated_rewards = session.get('updatedReward')
        if updated_rewards:
            store = session['store']
            mod_rewards = store.get("rewards")
            for reward in updated_rewards:
                for i, mreward in enumerate(mod_rewards):
                    # [{"reward_name":"Free bottle of wine", 
                    # "description":"Must be under $25 in value",
                    # "punches":10,"redemption_count":0,reward_id:0},]
                    if reward['reward_id']==mreward['reward_id']:
                        if reward.has_key("redemption_count"):
                            mod_rewards[i]['redemption_count'] =\
                                reward['redemption_count']
                        if reward.has_key("reward_name"):
                            mod_rewards[i]['reward_name'] =\
                                reward['reward_name']
                        if reward.has_key("punches"):
                            mod_rewards[i]['punches'] =\
                                reward['punches']
                        if reward.has_key("description"):
                            mod_rewards[i]['description'] =\
                                reward['description']
                        break
            data['rewards'] = updated_rewards
            store.rewards = mod_rewards
            session['store'] = store
            session['updatedReward'] = None
            
        #############################################################
        # REWARDS DELETED ##############################
        deleted_rewards = session.get("deletedReward")
        if deleted_rewards:
            store = session['store']
            rewards = store.get("rewards")
            rewards_ids = [ r['reward_id'] for r in rewards ]
            for reward in deleted_rewards:
                if reward['reward_id'] in rewards_ids:
                    for i, r in enumerate(rewards):
                        if r['reward_id'] == reward['reward_id']:
                            rewards.pop(i)
                            break
            store.rewards = rewards
            session['store'] = store
            session['deletedReward'] = None
           
        #############################################################
        # PATRONSTORE_COUNT ##################################
        patronStore_count_new = session.get('patronStore_num')
        if patronStore_count_new:
            patronStore_count_new = int(patronStore_count_new)
            data['patronStore_count'] = patronStore_count_new
            session['patronStore_count'] = patronStore_count_new
            session['patronStore_num'] = None
            """ Done in an daily cron job!
            # flag the emailing sequence patronStore_num > store limit
            sub = session['subscription']
            # subscriptionType 2 is highest sub, 0 free
            if sub.get("subscriptionType") != 2 and\
                not sub.get("date_passed_user_limit"):
                # now check if we passed the user limit for the sub
                user_limit =\
                    sub_type[sub.get("subscriptionType")]['max_users']
                if patronStore_count_new > user_limit:
                    sub.set("date_passed_user_limit",
                        timezone.now())
                    sub.update()
                    
            session['subscription'] = sub
            """

        # IMPORTANT! The request.session is the same as the 
        # SessionStore(session_key)! so we must use the 
        # request.session because it is automatically saved at the end
        # of each request- thereby overriding/undoing any changes made
        # to the SessionStore(session_key) key!
        request.session.update(\
            SessionStore(request.session.session_key))
        
        try: # respond
            return HttpResponse(json.dumps(data), 
                        content_type="application/json")
        except (IOError, socket.error) as e: # broken pipe/socket. 
            thread.exit() # exit silently
            
    # get the timestamp
    t = parser.parse(request.GET["timestamp"])
    timestamp = str(t.hour).zfill(2) + ":" +\
        str(t.minute).zfill(2) + ":" + str(t.second).zfill(2)
        
    # register the comet session
    CometSession.objects.update()
    CometSession.objects.create(session_key=\
        request.session.session_key, timestamp=timestamp,
        store_id=request.session['store'].objectId)
    
    # cache the current session at this state
    session_copy = request.session.copy()
    comet_time = session_copy['comet_time']
    timeout_time = comet_time + relativedelta(seconds=REQUEST_TIMEOUT)
    
    # keep going until its time to return a response forcibly
    while timezone.now() < timeout_time:  
        # need to update he objects manager to get the latest objects
        CometSession.objects.update() 
        try:     
            scomet = CometSession.objects.get(session_key=\
                request.session.session_key,timestamp=timestamp):
        except CometSession.DoesNotExist:
            # cometsession was deleted - time to go
            try:
                # make sure that the latest session is saved!
                request.session.update(\
                    SessionStore(request.session.session_key))
                return HttpResponse(json.dumps({"result":-1}), 
                            content_type="application/json")
            except (IOError, socket.error) as e: 
                thread.exit() 
                
        if scomet.modified:
            # delete the registered comet session object
            CometSession.objects.update()
            try:
                scomet = CometSession.objects.get(session_key=\
                    request.session.session_key, timestamp=timestamp)
                scomet.delete()
            except CometSession.DoesNotExist:
                pass # do nothing
            return comet(session)
        else: # nothing new, sleep for a bit
            sleep(COMET_REFRESH_RATE)
            
    # TIME IS UP - return a response result 0 means no change 
            
    # make sure that request.session is the most up to date
    session = SessionStore(request.session.session_key)
    request.session.update(session)
    
    try:
        return HttpResponse(json.dumps({"result":0}), 
                        content_type="application/json")
    except (IOError, socket.error) as e:
        thread.exit() # exit silently
        
@login_required
def terminate(request):
    """
    Flags the looping thread in refresh view to exit.
    This simply deletes the CometSession bound to this instance.
    """
    if request.method == "GET" or request.is_ajax():
        t = parser.parse(request.GET["timestamp"])
        timestamp = str(t.hour).zfill(2) + ":" +\
            str(t.minute).zfill(2) + ":" + str(t.second).zfill(2)
        try:
            scomet = CometSession.objects.get(session_key=\
                request.session.session_key, timestamp=timestamp)
            scomet.delete()
        except CometSession.DoesNotExist:
            pass # do nothing
        
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
                Use request.raw_post_data instead!
    
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
        
    Note that since each CometSession is no longer unique to 1 session
    we need to keep track of the session_keys that have already been 
    processed to avoid duplication.     
        
    """
    if request.method == "POST" or request.is_ajax():
        postDict = json.loads(request.raw_post_data)
        skip = []
        for scomet in CometSession.objects.filter(store_id=store_id):
            # flag all threads with this session_key that new stuff
            scomet.modified = True
            scomet.save() 
            
            # do not process the same session again
            if session.scomet.session_key in skip:
                continue
            skip.append(scomet.session_key)
            
            # get the latest session associated with this object
            session = SessionStore(scomet.session_key)
            # TODO FIX THIS UP
            for key, value in postDict.iteritems():
                if key not in session or session.get(key) is None:
                    # keys ending with _num is a number
                    if key.endswith("_num") or key.endswith("_count"):
                        session[key] = value
                    # only 1 dict can exist
                    elif key.endswith("_one"):
                        session[key] = value # separated for clarity
                    # everything else is a list of dicts
                    else:
                        session[key] = [value]
                else:
                    # keys ending with _num is a number
                    if key.endswith("_num"):
                        session[key] = value
                    # keys ending in _count is a number that is added
                    elif key.endswith("_count"):
                        session[key] = session[key] + value
                    # only 1 dict can exist
                    elif key.endswith("_one"):
                        session[key] = value
                    # everything else is a list of dicts
                    else:
                        lst = session[key]
                        lst.append(value)
                        session[key] = lst
                        
            # need to save session to commit modifications
            session.modified = True
            session.save()
            
        return HttpResponse("success")
    return HttpResponse("error")
    
    
    
    
    
    
    
    
    
    
    








