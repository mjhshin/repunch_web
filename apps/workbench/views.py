from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from dateutil.tz import tzutc
from math import ceil
import json

from libs.dateutil.relativedelta import relativedelta
from parse.utils import cloud_call
from parse.auth.decorators import login_required
from parse import session as SESSION
from repunch.settings import PAGINATION_THRESHOLD

@login_required
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
    
    redemps = SESSION.get_redemptions(request.session)
    past_redemps = SESSION.get_redemptions_past(request.session)
    
    # initially display the first 20 pending/history chronologically
    redemps.sort(key=lambda r: r.createdAt, reverse=True)
    past_redemps.sort(key=lambda r: r.updatedAt, reverse=True)
    
    data['redemptions'] = redemps[:PAGINATION_THRESHOLD]
    data['past_redemptions'] = past_redemps[:PAGINATION_THRESHOLD]
    
    data["pag_threshold"] = PAGINATION_THRESHOLD
    data["pag_page"] = 1
    data["pending_redemptions_count"] = len(redemps)
    data["history_redemptions_count"] = len(past_redemps)
    
    return render(request, 'manage/workbench.djhtml', data)
    
@login_required
def get_page(request):
    """
    Returns a generated html to plug in the tables.
    """
    if request.method == "GET" or request.is_ajax():
        type = request.GET.get("type")
        page = int(request.GET.get("page")) - 1
        if type == "pending-redemptions":
            template = "manage/redemptions_pending_chunk.djhtml" 
            pending_redemps = SESSION.get_redemptions(request.session)
            # sort
            header_map = {
                "redemption_time":"createdAt",
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
            data = {"redemptions":pending_redemps[start:end]}
            
            request.session["redemptions"] = pending_redemps
            
        elif type == "history-redemptions":
            template = "manage/redemptions_history_chunk.djhtml"
            past_redemps =\
                SESSION.get_redemptions_past(request.session)
            # sort
            header_map = {
                "redemption_time-past":"createdAt",
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
    
@login_required
def redeem(request):
    """ returns json object. result is 0 if fail, 1 if success """
    if request.method == "GET" or request.is_ajax():
        redeemId = request.GET.get('redeemRewardId')
        rewardId = request.GET.get('rewardId') # as string
        store = SESSION.get_store(request.session)
        res = cloud_call("validate_redeem", {
                "redeem_id":redeemId,
                "store_id":store.get("objectId"),
                "reward_id":rewardId,
                })
                
        if 'error' not in res:
            redemptions = SESSION.get_redemptions(request.session)
            i_remove, result = -1, res.get("result")
            # remove from redemptions
            for i, red in enumerate(redemptions):
                if red.objectId == redeemId:
                    i_remove = i 
                    break
            if i_remove != -1:
                redemptions_past =\
                    SESSION.get_redemptions_past(request.session)
                if result and result == "insufficient":
                    redemptions.pop(i_remove).delete()
                else:
                    redemption = redemptions.pop(i_remove)
                    redemption.is_redeemed = True
                    redemptions_past.append(redemption)
                    request.session['redemptions_past'] =\
                        redemptions_past
                request.session['redemptions'] = redemptions
            
            if result and result == "insufficient":
                return HttpResponse(json.dumps({"result":2}), 
                            content_type="application/json")
            else:
                return HttpResponse(json.dumps({"result":1}), 
                            content_type="application/json")
                        
    return HttpResponse(json.dumps({"result":0}), 
                    content_type="application/json")
                       
