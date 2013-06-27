from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth import SESSION_KEY
from django.utils import timezone
from time import sleep
import json, thread

from libs.dateutil.relativedelta import relativedelta
from parse.utils import cloud_call
from parse.auth import login
from parse.apps.employees import PENDING
from parse.auth.decorators import login_required
from parse.apps.messages.models import Message
from parse.apps.employees.models import Employee
from parse.apps.rewards.models import RedeemReward
from parse import session as SESSION
from apps.accounts.forms import LoginForm
from repunch.settings import REQUEST_TIMEOUT, COMET_REFRESH_RATE,\
RETAILER_REFRESH_TIMEOUT

# TODO implement comet approach properly   
@login_required
def manage_refresh(request):
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
            "feedback_unread": SESSION.get_feedback_unread(\
                                    request.session),
            "feedback_unread_ids": feedback_unread_ids,
            "employees_pending": SESSION.get_employees_pending(\
                                    request.session),
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
        # feedback_unread
        feedbacks = results.get('feedbacks')
        if feedbacks:
            data['feedbacks'] = []
            for feedback in feedbacks:
                m = Message(**feedback)
                messages_received_list.insert(0, m)
                data['feedbacks'].append(m.jsonify())
            request.session['messages_received_list'] =\
                messages_received_list
            feedback_unread = 0
            for each in messages_received_list:
                if not each.is_read:
                    feedback_unread += 1
            data['feedback_unread'] = feedback_unread
            request.session['feedback_unread'] = feedback_unread
        # employees_pending
        employees = results.get("employees")
        if employees:
            data['employees'] = []
            for emp in employees:
                e = Employee(**emp)
                employees_pending_list.insert(0, e)
                data['employees'].append(e.jsonify())
            request.session['employees_pending_list'] =\
                employees_pending_list
            employees_pending = len(employees_pending_list)
            data['employees_pending'] = employees_pending
            request.session["employees_pending"] = employees_pending
        # redemptions
        reds, redemps = results.get("redemptions"), []
        if reds:
            for r in reds:
                rr = RedeemReward(**r)
                redemptions.insert(0, rr)
                request.session['redemptions'] = redemptions
                redemps.append(rr.jsonify())
                # make sure redemptions don't go past 20
                while len(redemptions) > 20:
                    redemptions.pop()
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
        
    return comet()

def manage_login(request):
    """
    Handle s ajax request from login-dialog.
    returns a json object with a code.
    Or renders the dedicated login page if manually enterd url.
    code 
       -1 - invalid request
        0 - invalid form input
        1 - bad login credentials
        2 - subscription is not active
        3 - success
    """
    data = {"code":-1}
    if request.method == 'POST' or request.is_ajax():
        form = LoginForm(request.POST)
        if form.is_valid(): 
            c = login(request, request.POST.dict().copy())
            c_type = type(c)
            if c_type is int:
                if c == 0:
                    data['code'] = 1 
                elif c == 1:
                    data['code'] = 2
            else:
                data['code'] = 3
        else:
            data['code'] =  0        
    else:
        if request.session.get('account'):
            return redirect(reverse('store_index'))
        data['form'] = LoginForm()
        return render(request, 'manage/login.djhtml', data)

    return HttpResponse(json.dumps(data), 
        content_type="application/json")

def manage_logout(request):
    # need to clear the session
    request.session.flush()
    return redirect(reverse('public_home'))

def manage_terms(request):
    return render(request, 'manage/terms.djhtml')

