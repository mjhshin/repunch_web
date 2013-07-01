from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
import json

from parse import session as SESSION
from parse.utils import cloud_call
from parse.apps.messages.models import Message
from parse.apps.employees.models import Employee
from parse.auth.decorators import login_required
from parse.apps.messages.models import Message
from parse.apps.employees.models import Employee
from parse.apps.rewards.models import RedeemReward
from repunch.settings import REQUEST_TIMEOUT, COMET_REFRESH_RATE,\
RETAILER_REFRESH_TIMEOUT


# TODO implement comet approach properly   
@login_required
def refresh(request):
    """
    This is where the comet approach is put into play.
    This handles ajax requests from clients, holding on to the 
    request while checking Parse for new activity.
    """
    # in_time = timezone.now()
    # out_time = in_time + relativedelta(seconds=REQUEST_TIMEOUT)
    def comet():
        # sleep(COMET_REFRESH_RATE)
        # prep the params
        store = SESSION.get_store(request.session)
        redemptions = SESSION.get_redemptions(request.session)
        redemption_ids = []
        feedback_unread_ids, employees_pending_ids = [], []
        messages_received_list =\
            SESSION.get_messages_received_list(request.session)
        for fb in messages_received_list:
            if not fb.get('is_read'):
                feedback_unread_ids.append(fb.objectId)
        employees_pending_list =\
            SESSION.get_employees_pending_list(request.session)
        for emp in employees_pending_list:
            if emp.get('status') == PENDING:
                employees_pending_ids.append(emp.objectId)
        for red in redemptions:
            redemption_ids.append(red.objectId)
                
        # make the call
        res = cloud_call("retailer_refresh", {
            "store_id": store.objectId,
            "rewards": store.get('rewards'),
            "patronStore_count": SESSION.get_patronStore_count(\
                                    request.session),
            "feedback_unread_ids": feedback_unread_ids,
            "employees_pending_ids": employees_pending_ids,
            "redemption_ids": redemption_ids,
        }, timeout=RETAILER_REFRESH_TIMEOUT)
        
        # process results
        data = {}
        results = res['result']
        # rewards redemption_count
        rewards = results.get('rewards')
        mod_rewards = store.get('rewards')
        if rewards and len(rewards) > 0:
            for reward in rewards:
                for i, mreward in enumerate(mod_rewards):
                    if reward['reward_name']==mreward['reward_name']:
                        mod_rewards[i]['redemption_count'] =\
                            reward['redemption_count']
                        break
            data['rewards'] = rewards
            store.rewards = mod_rewards
            request.session['store'] = store
        # patronStore_count
        patronStore_count = results.get('patronStore_count')
        if patronStore_count:
            data['patronStore_count'] = patronStore_count
            request.session['patronStore_count'] = patronStore_count
        # feedbacks
        feedbacks = results.get('feedbacks')
        if feedbacks:
            data['feedbacks'] = []
            for feedback in feedbacks:
                m = Message(**feedback)
                messages_received_list.insert(0, m)
                data['feedbacks'].append(m.jsonify())
            request.session['messages_received_list'] =\
                messages_received_list
            fb_count = 0
            for fb in messages_received_list:
                if not fb.get("is_read"):
                    fb_count += 1
            data['feedback_unread'] = fb_count
        # employees
        employees = results.get("employees")
        if employees:
            data['employees'] = []
            for emp in employees:
                e = Employee(**emp)
                employees_pending_list.insert(0, e)
                data['employees'].append(e.jsonify())
            request.session['employees_pending_list'] =\
                employees_pending_list
            data['employees_pending'] = len(employees_pending_list)
        # redemptions
        reds, redemps = results.get("redemptions"), []
        if reds:
            for r in reds:
                rr = RedeemReward(**r)
                redemptions.insert(0, rr)
                request.session['redemptions'] = redemptions
                redemps.append(rr.jsonify())
            data['redemption_count'] = len(redemptions)
            data['redemptions'] = redemps
        """
        print results, timezone.now()
        if timezone.now() < request.session.get('comet_dead_time'):
            thread.exit()
            return # unreachable code
        elif len(results) < 2 and timezone.now() < out_time:
            # will force to ping back request after out_time!
            return comet()
        """
        
        try:
            resp = HttpResponse(json.dumps(data), 
                        content_type="application/json")
            return resp
        except IOError: # broken pipe or something. 
            # exit silently
            thread.exit()
            
    def new_session_comet():
        """ returns a new session comet with new expiration """
        pass
    """ 
    try:
        scomet = SessionComet.objects().get(sessionId=\
            request.session[SESSION_KEY])
        if scomet.changes:
            return comet()
        return HttpResponse(json.dumps({"result":"none"}), 
                        content_type="application/json")
    except SessionComet.DoesNotExist:
        # create it here and call comet
        
        return comet()
    else:  
    """ 
    return comet()
