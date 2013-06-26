from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from dateutil.tz import tzutc
import json

from libs.dateutil.relativedelta import relativedelta
from parse.utils import cloud_call
from parse.auth.decorators import login_required
from parse import session as SESSION

@login_required
def index(request):
    # do not just use timezone.now(). that will just get the current
    # utc time. We need the local time and then convert it to utc
    today = timezone.make_aware(datetime.now(), 
                    SESSION.get_store_timezone(request.session))
    yesterday = today + relativedelta(days=-1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0)
    yesterday = timezone.localtime(yesterday, tzutc())
    data = {"workbench_nav":True,
        "redemptions":SESSION.get_redemptions(request.session),
        "settings":SESSION.get_settings(request.session),
        "yesterday":yesterday}
    return render(request, 'manage/workbench.djhtml', data)
    
@login_required
def redeem(request):
    """ returns json object. result is 0 if fail, 1 if success """
    if request.method == "GET" or request.is_ajax():
        redeemId = request.GET.get('redeemRewardId')
        res = cloud_call("validate_redeem", {"redeem_id":\
                redeemId})
                
        if 'error' not in res:
            redemptions = SESSION.get_redemptions(request.session)
            i_remove = -1
            for i, red in enumerate(redemptions):
                if red.objectId == redeemId:
                    i_remove = i
                    break
            if i_remove != -1:
                redemptions.pop(i_remove)
                request.session['redemptions'] = redemptions
                    
            return HttpResponse(json.dumps({"result":1}), 
                        content_type="application/json")
                        
    return HttpResponse(json.dumps({"result":0}), 
                    content_type="application/json")
                       
