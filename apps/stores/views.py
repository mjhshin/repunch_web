from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http.request import QueryDict
from django.http import HttpResponse
from django.forms.models import inlineformset_factory
from datetime import datetime
import json

from apps.stores.models import Store as dStore, Hours as dHours
from apps.stores.forms import StoreForm, StoreAvatarForm
from libs.repunch.rphours_util import HoursInterpreter

from parse import session as SESSION
from parse.utils import delete_file, create_png, cloud_call
from parse.apps.stores.models import Store
from parse.auth.decorators import login_required

@login_required
def punch(request):
    if request.method == "POST" or request.is_ajax():
        store = SESSION.get_store(request.session)
        data = {
            "store_id":store.objectId,
            "store_name":str(store.get('store_name')),
            "punch_code":str(request.POST['punch_code']),
            "num_punches":int(request.POST['num_punches']),
        }
        res = cloud_call("punch", data)
        return HttpResponse(json.dumps(res), 
                content_type="application/json")
    else:
        return HttpResponse(json.dumps({u'code': 141,
                u'error': u'error'}), content_type="application/json")

@login_required
def index(request):
    data = {'account_nav': True}
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/store_details.djhtml', data)

@login_required
def edit(request):
    data = {'account_nav': True}
    store = SESSION.get_store(request.session)
    # fake a store to construct HoursFormset - probably not necessary
    dstore_inst = dStore()
            
    if request.method == 'POST': 
        HoursFormSet = inlineformset_factory(dStore, dHours,
                            max_num=7, extra=0)
        formset = HoursFormSet(request.POST, prefix='hours',
                                instance=dstore_inst) 
        form = StoreForm(request.POST)
        if form.is_valid(): 
            store = Store(**store.__dict__)
            store.update_locally(request.POST.dict(), False)
            
            # build the list of hours in proper format for saving 
            # to Parse
            hours, ind, key = [], 0, "hours-0-days"
            while ind < 7:
                days = request.POST.getlist(key)
                if days and not request.POST.get('hours-' +\
                        str(ind) + '-DELETE'):
                    # format time from 10:00:00 to 1000
                    open_time = request.POST["hours-" + str(ind) +\
                                "-open"].replace(":", "").zfill(6)[:4]
                    close_time = request.POST["hours-" + str(ind) +\
                                "-close"].replace(":", 
                                                "").zfill(6)[:4]
                    for day in days:
                        hours.append({
                            "day":int(day)-1, # days are from 0 to 6
                            "open_time":open_time,
                            "close_time":close_time,
                        })
                ind += 1
                key = "hours-" + str(ind) + "-days"
            store.set("hours", hours)
            store.update()

            data['success'] = "Store details have been saved."
    else:
        form = StoreForm()
        form.initial = store.__dict__
        
    hours_map = {}
    # group up the days that aare in the same row
    # also need to shift days frm 0-6 to 1-7
    if store.get("hours"):
        for hour in store.get("hours"):
            key = (hour['close_time'], hour['open_time'])
            if key in hours_map:
                hours_map[key].append(unicode(hour['day']+1))
            else:
                hours_map[key] = [unicode(hour['day']+1)]
            
    # create the formset
    HoursFormSet = inlineformset_factory(dStore, dHours,
                        max_num=7, extra=len(hours_map))
    formset = HoursFormSet(prefix='hours', instance=dstore_inst)
    # set forms in formset initial data
    for i, key in enumerate(hours_map.iterkeys()):
        d = {'days':hours_map[key],
                'open':unicode(key[1][:2] +\
                        ':' + key[1][2:4] + ':00'),
                'close':unicode(key[0][:2] +\
                        ':' + key[0][2:4] + ':00'),
                'list_order':unicode(i+1) }
        formset[i].initial = d
            
    # update the session cache
    request.session['store'] = store
       
    data['form'] = form
    data['hours_formset'] = formset

    return render(request, 'manage/store_edit.djhtml', data)

@login_required
def hours_preview(request):
    HoursFormSet = inlineformset_factory(dStore, dHours, extra=0)
    
    hours = []
    formset = HoursFormSet(request.GET, prefix='hours', 
                            instance=dStore())
    if formset.is_valid():
        for form in formset:
            if(not 'DELETE' in form.changed_data):
                hours.append(form.instance)
    
    return HttpResponse(HoursInterpreter(hours).readable(), 
                        content_type="text/html")
    
    
@login_required
def avatar(request):
    data = {}
    store = SESSION.get_store(request.session)
    
    if request.method == 'POST': 
        form = StoreAvatarForm(request.POST, request.FILES)
        if form.is_valid():
            # need to remove old file
            if store.get('store_avatar'):
                delete_file(store.store_avatar, 'png')
                
            res = create_png(request.FILES['store_avatar'])
            if res and 'error' not in res:
                store.store_avatar = res.get('name')
                store.store_avatar_url = res.get('url')
            store.update()
            
            data['success'] = True
    else:
        form = StoreAvatarForm();
    
    # update the session cache
    request.session['store'] = store
    
    data['form'] = form
    data['url'] = reverse('store_avatar')
    return render(request, 'manage/avatar_upload.djhtml', data)
