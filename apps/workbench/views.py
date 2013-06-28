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
    redemps = SESSION.get_redemptions(request.session)[:20]
    past_redemps = SESSION.get_redemptions_past(request.session)[:20]
    data = {"workbench_nav":True,
        "redemp_pages":ceil(float(len(redemps))/20.0),
        "past_redemp_pages":ceil(float(len(past_redemps))/20.0),
        "redemptions":redemps,
        "settings":SESSION.get_settings(request.session),
        "past_redemptions":past_redemps,
        "today":today}
    return render(request, 'manage/workbench.djhtml', data)
    
@login_required
def get_redemp_page(request):
    """
    Returns a generated html to plug in the tables.
    """
    if request.method == "GET" and request.is_ajax():
        pass
    return render(request, 'manage/redemptions.djhtml', data)
    
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
            i_remove = -1
            # remove from redemptions
            for i, red in enumerate(redemptions):
                if red.objectId == redeemId:
                    i_remove = i
                    break
            if i_remove != -1:
                redemptions_past =\
                    SESSION.get_redemptions_past(request.session)
                redemption = redemptions.pop(i_remove)
                redemption.is_redeemed = True
                redemptions_past.append(redemption)
                request.session['redemptions_past'] = redemptions_past
                request.session['redemptions'] = redemptions
            
            return HttpResponse(json.dumps({"result":1}), 
                        content_type="application/json")
                        
    return HttpResponse(json.dumps({"result":0}), 
                    content_type="application/json")
                       
