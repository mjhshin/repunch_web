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
    # in_time = timezone.now()
    # out_time = in_time + relativedelta(seconds=REQUEST_TIMEOUT)
    def comet(session_key):
        # sleep(COMET_REFRESH_RATE)
        store = SESSION.get_store(request.session)
        
        # used by more than 1 (note that it is ok to retrieve all of 
        # the lists since they are all pointers - not the actual list!
        employees_pending_list =\
            SESSION.get_employees_pending_list(request.session)
        employees_approved_list =\
            SESSION.get_employees_approved_list(request.session)
        messages_received_list =\
            SESSION.get_messages_received_list(request.session)
        redemptions_pending =\
            SESSION.get_redemptions_pending(request.session)
        redemptions_past =\
            SESSION.get_redemptions_past(request.session)
            
        # get the session
        session = SessionStore(scomet.session_key)
        
        # process the stuff in the session
        data = {}
        
        #############################################################
        # REWARDS redemption_count ##############################
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
            
        #############################################################
        # PATRONSTORE_COUNT ##################################
        patronStore_count_new = session.get('patronStore_num')
        if patronStore_count_new:
            # TODO patronStore_num > store limit then upgrade account
            # and send email notification make sure to update the
            # subscription in the cache afterwards!
            data['patronStore_count'] = patronStore_count_new
            request.session['patronStore_count']=patronStore_count_new
            del session['patronStore_num']
       
        # MESSAGE SENT ##################################
        messages_sent = session.get("newMessage")
        if messages_sent:
            messages_sent_list =\
                SESSION.get_messages_sent_list(request.session)
            messages_sent_ids =\
                [ msg.id for msg in messages_sent_list ]
            for message in messages_sent:
                m = Message(**feedback)
                if m.objectId not in messages_sent_ids:
                    messages_sent_list.insert(0, m)
            request.session['messages_sent_list'] = messages_sent_list
            del session['newMessage']
        
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
                
            request.session['messages_received_list'] =\
                messages_received_list
            del session['newFeedback']

        #############################################################
        # FEEDBACK DELETED ##################################
        feedbacks_deleted = session.get("deletedFeedback")
        if feedbacks_deleted:
            copy = messages_received_list[:]
            for fb_d in feedbacks_deleted:
                fb = Message(**fb_d)
                for i, mro in enumerate(copy):
                    if fb.objectId == mro.objectId:
                        messages_received_list.pop(i)
                        break
            request.session['messages_received_list'] =\
                messages_received_list
            del session['deletedFeedback']            
        
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
                
            request.session['employees_pending_list'] =\
                employees_pending_list
            del session['pendingEmployee']
        
        #############################################################
        # EMPLOYEES APPROVED (pending to approved) #################
        appr_emps = session.get("approvedEmployee")
        if appr_emps:
            copy = employees_pending_list[:]
            for appr_emp in appr_emps:
                emp = Employee(**appr_emp)
                # first check if the employee is in the pending list
                # if not then check if it is already approved
                for i, emp_pending in enumerate(copy):
                    if emp.objectId == emp_pending.objectId:
                        emp = employees_pending_list.pop(i)
                        emp.status = APPROVED
                        employees_approved_list.insert(0, emp)
                        break
            request.session['employees_pending_list'] =\
                employees_pending_list
            request.session['employees_approved_list'] =\
                employees_approved_list
            del session['approvedEmployee']
            
        #############################################################
        # EMPLOYEES DELETED/DENIED/REJECTED (pending/approved to pop)!
        del_emps = session.get("deletedEmployee")
        if del_emps:
            approved_copy = employees_approved_list[:]
            pending_copy = employees_pending_list[:]
            for demp in del_emps:
                emp = Employee(**demp)
                cont = True
                # check in approved emps
                for i, cop in enumerate(approved_copy):
                    if cop.objectId == emp.objectId:
                        employees_approved_list.pop(i)
                        cont = False
                        break
                    
                if not cont:
                    break
                    
                # check in pending emps
                for i, cop in enumerate(pending_copy):
                    if cop.objectId == emp.objectId:
                        employees_pending_list.pop(i)
                        break
                        
            request.session['employees_approved_list'] =\
                employees_approved_list
            request.session['employees_pending_list'] =\
                employees_pending_list
            del session['deletedEmployee']
         
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
            del session['updatedEmployeePunch']
           
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
                
            request.session['redemptions_pending'] =\
                redemptions_pending
            del session['pendingRedemption']
            
        """
        + patronStore_num = request.POST.get("patronStore_num")
        + updatedReward = request.POST.get("updatedReward")
        + newMessage = request.POST.get("newMessage")
        + newFeedback = request.POST.get("newFeedback")
        + deletedFeedback = request.POST.get("deletedFeedback")
        + pendingEmployee = request.POST.get("pendingEmployee")
        + approvedEmployee = request.POST.get("approvedEmployee")
        + deletedEmployee = request.POST.get("deletedEmployee")
        + updatedEmployeePunch =request.POST.get("updatedEmployeePunch")
        + pendingRedemption = request.POST.get("pendingRedemption")
        + approvedRedemption = request.POST.get("approvedRedemption")
        deletedRedemption = request.POST.get("deletedRedemption")
        """ 
        #############################################################
        # REDEMPTIONS APPROVED (pending to history)
        appr_redemps = session.get("approvedRedemption") 
        if appr_redemps:   
            copy = redemptions_pending[:]
            redemp_js = []
            for red in appr_redemps:
                redemp = RedeemReward(**red)
                # check if redemp is still in pending
                for i, redem in enumerate(copy):
                    if redem.objectId == redemp.objectId:
                        r = redemptions_pending.pop(i)
                        r.is_redeemed = True
                        redemptions_past.insert(0, r)
                        redemp_js = append(r)
                        break
                # if not then check if it is in the history already
                # the above shouldn't happen!
            if len(redemp_js) > 0:
                data['redemptionsApproved'] = redemp_js
                
            request.session['redemptions_pending'] =\
                redemptions_pending
            request.session['redemptions_past'] =\
                redemptions_past
            del session['approvedRedemption']
        
        
        #############################################################
        ######## make sure to update the session!
        session.save()
        try: # respond
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
    
        patronStore_num = request.POST.get("patronStore_num")
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
    
    
    
    
    
    
    
    
    
    
    








