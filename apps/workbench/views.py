from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.sessions.backends.cache import SessionStore
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from dateutil.tz import tzutc
from math import ceil
import json

from libs.dateutil.relativedelta import relativedelta
from parse.utils import cloud_call
from parse.comet import comet_receive
from parse.apps.rewards.models import RedeemReward
from parse.decorators import access_required
from parse.auth.decorators import login_required, dev_login_required
from parse import session as SESSION
from repunch.settings import PAGINATION_THRESHOLD, DEBUG,\
COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY

@dev_login_required
@login_required
@access_required
def index(request):
    """
    Renders the first 20 most recent pending and approved/denied
    redemptions.
    """
    # do not just use timezone.now(). that will just get the current
    # utc time. We need the local time and then convert it to utc
    today = timezone.make_aware(datetime.now(), 
                    SESSION.get_store_timezone(request.session))
    today = today + relativedelta(days=-1)
    today = today.replace(hour=23, minute=59, second=59) # midnight
    
    data = {"workbench_nav":True, "settings":\
        SESSION.get_settings(request.session), "today":today}
    
    redemps = SESSION.get_redemptions_pending(request.session)
    past_redemps = SESSION.get_redemptions_past(request.session)
    
    # initially display the first 20 pending/history chronologically
    redemps.sort(key=lambda r: r.createdAt, reverse=True)
    past_redemps.sort(key=lambda r: r.updatedAt, reverse=True)
    
    data['pending_redemptions'] = redemps[:PAGINATION_THRESHOLD]
    data['past_redemptions'] = past_redemps[:PAGINATION_THRESHOLD]
    
    data["pag_threshold"] = PAGINATION_THRESHOLD
    data["pag_page"] = 1
    data["pending_redemptions_count"] = len(redemps)
    data["history_redemptions_count"] = len(past_redemps)
    
    return render(request, 'manage/workbench.djhtml', data)
    
@dev_login_required
@login_required
@access_required(http_response="<div class='tr'>Access denied</div>",\
content_type="text/html")
def get_page(request):
    """
    Returns a generated html to plug in the tables.
    """
    if request.method == "GET":
        type = request.GET.get("type")
        page = int(request.GET.get("page")) - 1
        if type == "pending-redemptions":
            template = "manage/redemptions_pending_chunk.djhtml" 
            pending_redemps =\
                SESSION.get_redemptions_pending(request.session)
            # sort
            header_map = {
                "redemption_time":"createdAt", # IMPORTANT DIFF!
                "redemption_customer_name": "customer_name",
                "redemption_title": "title",
                "redemption_punches": "num_punches",
            }
            header = request.GET.get("header")
            if header: # header can only be date
                reverse = request.GET.get("order") == "desc"
                pending_redemps.sort(key=lambda r:\
                    r.__dict__[header_map[header]], reverse=reverse)
            
            # set the chunk
            start = page * PAGINATION_THRESHOLD
            end = start + PAGINATION_THRESHOLD
            data = {"pending_redemptions":pending_redemps[start:end]}
            
            request.session["redemptions_pending"] = pending_redemps
            
        elif type == "history-redemptions":
            template = "manage/redemptions_history_chunk.djhtml"
            past_redemps =\
                SESSION.get_redemptions_past(request.session)
            # sort
            header_map = {
                "redemption_time-past":"updatedAt", # IMPORTANT DIFF!
                "redemption_customer_name-past": "customer_name",
                "redemption_title-past": "title",
                "redemption_punches-past": "num_punches", 
            }
            header = request.GET.get("header")
            if header:
                reverse = request.GET.get("order") == "desc"
                past_redemps.sort(key=lambda r:\
                    r.__dict__[header_map[header]], reverse=reverse)
                    
            request.session["redemptions_past"] = past_redemps
            # set the chunk
            start = page * PAGINATION_THRESHOLD 
            end = start + PAGINATION_THRESHOLD
            data = {"past_redemptions":past_redemps[start:end]}
       
        # don't forget the today for comparison!
        today = timezone.make_aware(datetime.now(), 
                    SESSION.get_store_timezone(request.session))
        today = today + relativedelta(days=-1)
        today = today.replace(hour=23, minute=59, second=59)
        
        data["today"] = today
        return render(request, template, data)
        
    return HttpResponse("Bad request")
    
@dev_login_required
@login_required
@access_required(http_response={"error":"permission_denied"})
def punch(request):
    if request.method == "POST":
        try:
            nump = int(request.POST['num_punches'])
        except ValueError:
            return HttpResponse(json.dumps({'error': 'float'}),
                content_type="application/json")
                
        settings = SESSION.get_settings(request.session)
        if nump > settings.get("punches_employee"):
            return HttpResponse(json.dumps({'error': 'over',
                'limit': nump}), content_type="application/json")
    
        store = SESSION.get_store(request.session)
        data = {
            "store_location_id":\
                SESSION.get_active_store_location_id(request.session),
            "store_id":store.objectId,
            "store_name":str(store.get('store_name')),
            "punch_code":str(request.POST['punch_code']),
            "num_punches":nump,
        }
        
        # Check if the user is an employee
        employee = request.session.get("employee")
        if employee:
            data['employee_id'] = employee.objectId
        
        res = cloud_call("punch", data)
        if 'error' not in res:
            res['patron_name'] = res['result']
            # always make sure to get the latest session since the session 
            # will be saved on return!!!            
            request.session.clear()        
            request.session.update(SessionStore(request.session.session_key))
            return HttpResponse(json.dumps(res), 
                    content_type="application/json")
        else:
            if res['error'] == "PATRON_NOT_FOUND":
                request.session.clear()        
                request.session.update(SessionStore(request.session.session_key))
                return HttpResponse(json.dumps({"error":\
                    "PATRON_NOT_FOUND"}), 
                    content_type="application/json")
            

    # always make sure to get the latest session since the session 
    # will be saved on return!!!     
    request.session.clear()                           
    request.session.update(SessionStore(request.session.session_key))
    return HttpResponse(json.dumps({'error': 'error'}),
        content_type="application/json")
    
@dev_login_required
@login_required
@access_required(http_response={"error":"permission_denied"})
def redeem(request):
    """ returns json object. result is 0 if fail, 1 if success,
    2 if insufficient punches, 3 if already validated, 
    4 if successfully deleted/denied, 5 has been deleted elsewhere and
    action is deny, 6 PatronStore has been removed,
    7 deleted elsewhere and action is approve.
    """
    if request.method == "GET":        
        # approve or deny
        action = request.GET.get("action")
        redeemId = request.GET.get('redeemRewardId')
        # may come in as "None" or "null" or "undefined"
        rewardId = request.GET.get('rewardId') 
        if str(rewardId).isdigit():
            rewardId = int(rewardId)
        else:
            rewardId = None
            
        store = SESSION.get_store(request.session)
        if action == "approve":
            res = cloud_call("validate_redeem", {
                    "redeem_id":redeemId,
                    "store_id":store.get("objectId"),
                    "reward_id":rewardId,
                    })
        elif action == "deny":
            res = cloud_call("reject_redeem", {
                    "redeem_id":redeemId,
                    "store_id":store.get("objectId"),
                    })
                    
        # retrieve latest session since user may click a bunch 
        # of redemptions consecutively
        session = SessionStore(request.session.session_key)
            
        data = {"result" : 0}
            
        # success result removed means patronstore is null!
        if 'error' not in res:
            redemptions_pending =\
                    SESSION.get_redemptions_pending(session)
            i_remove = -1
            if action == "approve":
                result = res.get("result").get("code")
                result_red =\
                    RedeemReward(**res.get("result").get("result"))
            else:
                result = res.get("result")
                
            # remove from redemptions_pending
            for i, red in enumerate(redemptions_pending):
                if red.objectId == redeemId:
                    i_remove = i 
                    break
           
            # IMPORTANT! Since comet receive  immediately commits
            # changes to a session, i_remove will probably be -1
            
            if action == "approve":
                redemptions_past =\
                    SESSION.get_redemptions_past(session)
                    
                if result and result in ("insufficient",
                    "PATRONSTORE_REMOVED") and i_remove != -1:
                    redemptions_pending.pop(i_remove)
                    
                elif i_remove != -1: # success
                    redemption = redemptions_pending.pop(i_remove)
                    redemption.is_redeemed = True
                    redemption.updatedAt = result_red.updatedAt 
                    redemptions_past.append(redemption)
                    session['redemptions_past'] =\
                        redemptions_past
                      
                # session changed only if i_remove was not 1
                if i_remove != -1: 
                    session['redemptions_pending'] =\
                        redemptions_pending
                
                if result and result == "insufficient":
                    data["result"] = 2
                elif result and result == "validated":
                    data["result"] = 3
                elif result and result == "PATRONSTORE_REMOVED":
                    data["result"] = 6
                else:
                    data["result"] = 1
                    
                # request.session will be saved after return
                request.session.clear()
                request.session.update(session)
                return HttpResponse(json.dumps(data), 
                            content_type="application/json")
                                
            elif action == "deny":
                if i_remove != -1:
                    del_red = redemptions_pending.pop(i_remove)
                    session['redemptions_pending'] =\
                        redemptions_pending
                        
                data["result"] = 4
               
                request.session.clear()
                request.session.update(session)
                return HttpResponse(json.dumps(data), 
                                content_type="application/json")
                                
        elif 'error' in res:
            if res['error'] == "REDEEMREWARD_NOT_FOUND":
                if action == "approve":
                    data["result"] = 7
                elif action == "deny":
                    data["result"] = 5
            elif res['error'] == "REDEEMREWARD_VALIDATED":
                data["result"] = 3
            elif res['error'] == "PATRONSTORE_REMOVED":
                data["result"] = 6
                        
    # always make sure to get the latest session since the session 
    # will be saved on return!!!       
    request.session.clear()             
    request.session.update(SessionStore(request.session.session_key))
    return HttpResponse(json.dumps(data), 
                    content_type="application/json")
                       
