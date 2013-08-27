"""
Contains functions used for comet connections.
"""
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.backends.cache import SessionStore
import pytz

from apps.comet.models import CometSession, CometSessionIndex
from repunch.settings import COMET_RECEIVE_KEY_NAME, TIME_ZONE,\
COMET_RECEIVE_KEY

from parse import session as SESSION
from parse.apps.messages import FEEDBACK
from parse.apps.messages.models import Message
from parse.apps.employees import APPROVED, DENIED
from parse.apps.employees.models import Employee
from parse.apps.rewards.models import RedeemReward
from parse.apps.stores.models import Store, Subscription, Settings

def comet_receive(store_id, postDict):
    """
    Returns True if the injection to the session and SessionComet
    is successful.
    
    Note that postDict must be contain values that are jsonified!
    
    This adds to the related session's cache:
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
        updatedPunchesFacebook_int
        
    Note that since each CometSession is no longer unique to 1 session
    we need to keep track of the session_keys that have already been 
    processed to avoid duplication.     
        
    """
            
    def processCometReceivedDict(session, postDict):
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
            store = Store(**updatedStore_one)
            session['store'] = store
            try: # also update the store_timezone
                session['store_timezone'] =\
                    pytz.timezone(store.get('store_timezone'))
            except Exception: # assign a default timezone
                session['store_timezone'] =\
                    pytz.timezone(TIME_ZONE)
            
        updatedStoreAvatarName_str =\
            postDict.get("updatedStoreAvatarName_str")
        if updatedStoreAvatarName_str:
            store = session['store']
            updatedStoreAvatarUrl_str =\
                postDict.get("updatedStoreAvatarUrl_str")
            if updatedStoreAvatarUrl_str:
                store.store_avatar_url = updatedStoreAvatarUrl_str
            store.store_avatar = updatedStoreAvatarName_str  
            session['store'] = store      
           
        # this is in the settings tab in the dashboard but the field
        # is in the Store class
        updatedPunchesFacebook_int =\
            postDict.get("updatedPunchesFacebook_int")
        if updatedPunchesFacebook_int:
            store = session['store']
            store.punches_facebook = int(updatedPunchesFacebook_int)
            session['store'] = store
            
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
                rewards.append(newReward)
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
    # check if key is present and valid
    if postDict.get(COMET_RECEIVE_KEY_NAME) != COMET_RECEIVE_KEY:
        return False
        
    for scomet in CometSessionIndex.objects.filter(\
        store_id=store_id):
        # get the latest session associated with this object
        session = SessionStore(scomet.session_key)
        # do not go if the session has already been logged out
        if session.get('account') is None or\
            SESSION_KEY not in session:
            continue
        processCometReceivedDict(session, postDict)
        
        # flag all threads with this session_key that new stuff
        CometSession.objects.update()
        for comet in CometSession.objects.filter(session_key=\
            scomet.session_key):
            comet.modified = True
            comet.save()
                    
        # need to save session to commit modifications
        session.modified = True
        session.save()
        
    return True
            
