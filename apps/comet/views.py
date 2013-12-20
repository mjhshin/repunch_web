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
from parse.utils import flush
from parse.decorators import access_required
from parse.auth.decorators import login_required, dev_login_required
from apps.comet.models import CometSession, CometSessionIndex
from parse.comet import comet_receive
from repunch.settings import REQUEST_TIMEOUT, COMET_PULL_RATE

@dev_login_required(http_response={"result": -3})
@login_required(http_response={"result": -3})
@access_required(http_response={"result":-2})
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
            pending = []
            for emp_id in employees_pending:
                for emp in employees_pending_list:
                    if emp.objectId == emp_id:
                        pending.append(emp.jsonify())
                        break
                    
            if len(pending) > 0:   
                data['employees_pending_count'] =\
                    len(employees_pending_list)
                data['employees_pending'] = pending
        
        #############################################################
        # EMPLOYEES APPROVED (pending to approved) #################
        emps_approved_copy = [ emp.objectId for emp in\
            employees_approved_list_copy]
        emps_approved = [ emp.objectId for emp in\
            employees_approved_list]
            
        appr_emps =\
            tuple(set(emps_approved) - set(emps_approved_copy))
        
        if appr_emps:
            approved = []
            for appr_emp_id in appr_emps:
                for emp in employees_approved_list:
                    if emp.objectId == appr_emp_id:
                        approved.append(emp.jsonify())
                        break
                        
            if len(approved) > 0:
                data['employees_approved'] = approved
                data['employees_pending_count'] =\
                    len(employees_pending_list)
            
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
            deleted = []
            for demp_id in del_emps:
                if demp_id in emps_approved_copy:
                    emps_list = employees_approved_list_copy
                else:
                    emps_list = employees_pending_list_copy
                    
                for emp in emps_list:
                    if emp.objectId == demp_id:
                        deleted.append(emp.jsonify())
                        break  
                        
            if len(deleted) > 0:   
                data['employees_pending_count'] =\
                    len(employees_pending_list)
                data['employees_deleted'] = deleted
           
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
            # Note that some rewards may have been deleted!
            rew = rewards.get(reward_id)
            if rew and rew_copy['redemption_count'] !=\
                rew['redemption_count']:
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
            
            
        #############################################################
        # ACTIVE_STORE_LOCATION_ID ############################
        data['active_store_location_id_changed'] =\
            session['active_store_location_id'] ==\
            session_copy['active_store_location_id']
            

        # IMPORTANT! The request.session is the same as the 
        # SessionStore(session_key)! so we must use the 
        # request.session because it is automatically saved at the end
        # of each request- thereby overriding/undoing any changes made
        # to the SessionStore(session_key) key!
        # need to check if we are still logged in
        session = SessionStore(request.session.session_key)
        if 'account' in session and SESSION_KEY in session:
            request.session.clear()
            request.session.update(session)
        else:
            flush(request.session)
        
        ############################################################
        # Respond ###########################################
        try: 
            return HttpResponse(json.dumps(data), 
                        content_type="application/json")
        except (IOError, socket.error) as e: # broken pipe/socket. 
            thread.exit() # exit silently
            
            
    ##################################################################
    ##### ENTRY POINT
    ######################################################
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
            request.session.session_key, 
            store_id=SESSION.get_store(request.session).objectId,
            last_updated=timezone.now())
        
        
    # register the CometSession
    CometSession.objects.update()
    CometSession.objects.create(session_key=\
        request.session.session_key, timestamp=timestamp, uid=uid)
    
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
                    request.session.clear()
                    request.session.update(session)
                else:
                    flush(request.session)
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
            try:
                return comet(session_copy)
            except KeyError:
                # if a key error occurs then that probably means that
                # the session has been flushed- was logged out by user
                # or forcefully by server =)
                # now time to flag existing tabs.
                request.session.clear()
                try: 
                    return HttpResponse(json.dumps({"result": -3}), 
                                content_type="application/json")
                except (IOError, socket.error) as e: # broken pipe/socket. 
                    thread.exit() # exit silently
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
        request.session.clear()
        request.session.update(session)
    else:
        flush(request.session)
    
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
        
@dev_login_required
@login_required
def terminate(request):
    """
    Flags the looping thread in the pull view to exit.
    This simply deletes the CometSession bound to this instance.
    """
    if request.method == "GET":
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
        request.session.clear()
        request.session.update(SessionStore(\
            request.session.session_key))
        
        return HttpResponse("ok")
    return HttpResponse("")
        
@csrf_exempt  
def receive(request, store_id):
    """
    Receives a get request from a foreign site and sets all of the 
    CometSessions that have the given store Id.
    This is called by a currently logged in user as well as by the
    cloud. Need to differentiate!
    
    Note: request.POST does not contain the data!
            Use request.body instead!
            
    Note 2: request.body comes in Latin-1 format (ISO-8859-1).
        This must be converted to unicode which will then be encoded
        to UTF-8 by django and the browser 
        (<meta http-equiv="Content-Type" content="text/html; charset=utf-8">)         
    """
    if request.method == "POST":
        try:
            postDict = json.loads(unicode(request.body, "ISO-8859-1"))
        except Exception:
            return HttpResponse("error")
        
        if comet_receive(store_id, postDict):
            return HttpResponse("success")
            
    return HttpResponse("error")
        


