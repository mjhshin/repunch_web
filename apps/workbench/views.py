from django.http import HttpResponse
from django.shortcuts import render
import json

from parse.utils import cloud_call
from parse.auth.decorators import login_required
from parse import session as SESSION

@login_required
def index(request):
    data = {"workbench_nav":True,
        "redemptions":SESSION.get_redemptions(request.session),
        "settings":SESSION.get_settings(request.session)}
    return render(request, 'manage/workbench.djhtml', data)
    
@login_required
def redeem(request):
    """ returns json object. result is 0 if fail, 1 if success """
    if request.method == "GET" or request.is_ajax():
        redeemId = request.GET.get('redeemRewardId')
        res = cloud_call("validate_redeem", {"redeem_id":\
                redeemId})
        print res
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
                       
