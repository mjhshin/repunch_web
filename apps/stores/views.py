from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.sessions.backends.cache import SessionStore
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http.request import QueryDict
from django.forms.models import inlineformset_factory
from datetime import datetime
from io import BytesIO
import json, urllib, urllib2, requests, os

from parse.decorators import session_comet
from apps.stores.models import Store as dStore, Hours as dHours,\
StoreAvatarTmp
from apps.stores.forms import StoreForm, StoreAvatarForm
from libs.repunch.rphours_util import HoursInterpreter
from libs.repunch.rputils import get_timezone, get_map_data

from repunch.settings import COMET_REQUEST_RECEIVE, MEDIA_ROOT
from parse.apps.patrons.models import Patron
from parse import session as SESSION
from parse.utils import delete_file, create_png, cloud_call
from parse.apps.stores.models import Store
from parse.apps.stores import format_phone_number
from parse.auth.decorators import login_required

@login_required
def punch(request):
    if request.method == "POST" or request.is_ajax():
        nump = int(request.POST['num_punches'])
        settings = SESSION.get_settings(request.session)
        if nump > settings.get("punches_employee"):
            return HttpResponse(json.dumps({u'code': 141,
                u'error': u'error'}), content_type="application/json")
    
        store = SESSION.get_store(request.session)
        data = {
            "store_id":store.objectId,
            "store_name":str(store.get('store_name')),
            "punch_code":str(request.POST['punch_code']),
            "num_punches":nump,
        }
        res = cloud_call("punch", data)
        if 'error' not in res:
            res['patron_name'] = res['result']
            return HttpResponse(json.dumps(res), 
                    content_type="application/json")

    return HttpResponse(json.dumps({u'code': 141,
            u'error': u'error'}), content_type="application/json")

@login_required
@session_comet
def index(request):
    data = {'account_nav': True}
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/store_details.djhtml', data)

@login_required
@session_comet
def edit(request):
    data = {'account_nav': True}
    store = SESSION.get_store(request.session)
    # fake a store to construct HoursFormset - probably not necessary
    dstore_inst = dStore()
    
    def common(form):
        hours_map = {}
        # group up the days that aare in the same row
        if store.get("hours"):
            for hour in store.get("hours"):
                key = (hour['close_time'], hour['open_time'])
                if key in hours_map:
                    hours_map[key].append(unicode(hour['day']))
                else:
                    hours_map[key] = [unicode(hour['day'])]
                
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
            
    if request.method == 'POST': 
        HoursFormSet = inlineformset_factory(dStore, dHours,
                            max_num=7, extra=0)
        formset = HoursFormSet(request.POST, prefix='hours',
                                instance=dstore_inst) 
        form = StoreForm(request.POST)
        if form.is_valid(): 
            # build the list of hours in proper format for saving 
            # to Parse. 
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
                        if int(open_time)>=int(close_time):
                            data["error"] = "Invalid hours. Open "+\
                                "time must be "+\
                                "greater than close time."
                            return common(form)
                        hours.append({
                            "day":int(day), 
                            "open_time":open_time,
                            "close_time":close_time,
                        })
                ind += 1
                key = "hours-" + str(ind) + "-days"
            
            store = Store(**store.__dict__)
            store.update_locally(request.POST.dict(), False)
            store.set("hours", hours)
            
            # set the timezone
            if store.get('zip'):
                store.store_timezone =\
                    get_timezone(store.get('zip')).zone
                    
            # format the phone number
            store.phone_number =\
                format_phone_number(request.POST['phone_number'])
            # update the store's coordinates and neighborhood
            full_address = " ".join(\
                store.get_full_address().split(", "))
            map_data = get_map_data(full_address)
            store.set("coordinates", map_data.get("coordinates"))
            store.set("neighborhood", 
                store.get_best_fit_neighborhood(\
                    map_data.get("neighborhood")))
                    
            store.update()
            # update the session cache
            request.session['store'] = store
            
            # notify other dashboards of this change
            payload = {"updatedStore_one":store.jsonify()}
            requests.post(COMET_REQUEST_RECEIVE + store.objectId,
                data=json.dumps(payload))
            
            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Store details has been updated.'}))
                
    else:
        form = StoreForm()
        form.initial = store.__dict__.copy()
        # make sure that the phone number is unformatted
        form.initial['phone_number'] =\
            form.initial['phone_number'].replace("(",
                "").replace(")","").replace(" ", "").replace("-","")
         
    return common(form)

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
        
            # save the file locallly
            avatar = form.save(request.session.session_key)
        
            """
            # need to remove old file
            if store.get('store_avatar'):
               delete_file(store.get("store_avatar"), 'png')
                
            # save the session before a cloud call!
            request.session.save()
            
            res = create_png(request.FILES['store_avatar'].file,
                request.FILES['store_avatar'].name)
                
            # make sure that we have the latest session
            session = SessionStore(request.session.session_key)
            store = SESSION.get_store(session)
            if res and 'error' not in res:
                store.store_avatar = res.get('name')
                store.store_avatar_url = res.get('url')
                request.session['has_store_avatar'] = True
            store.update()
            
            session["store"] = store
            request.session.update(session)
            """
            
            if avatar.width > avatar.height: # height is limiting
                center_width = avatar.width/2
                init_y1 = 0
                init_y2 = avatar.height
                init_x1 = center_width - avatar.height/2
                init_x2 = center_width + avatar.height/2
            else:
                center_height = avatar.height/2
                init_x1 = 0
                init_x2 = avatar.width
                init_y1 = center_height - avatar.width/2
                init_y2 = center_height + avatar.width/2
                
            data = {
                'avatar': avatar,
                'init_x1': init_x1,
                'init_y1': init_y1,
                'init_x2': init_x2,
                'init_y2': init_y2,
            }
            
            return render(request, 'manage/avatar_crop.djhtml', data)
            
    else:
        form = StoreAvatarForm()
    
    # update the session cache
    request.session['store'] = store
    
    data['form'] = form
    data['url'] = reverse('store_avatar')
    return render(request, 'manage/avatar_upload.djhtml', data)
    
@login_required
def get_avatar(request):
    """ returns the store's avatar url """
    if request.method == "GET" or request.is_ajax():
        store = SESSION.get_store(request.session)
        return HttpResponse(store.get("store_avatar_url"))
        

@login_required
def crop_avatar(request):
    """ takes in crop coordinates and creates a new png image """
            
    if request.method == "POST":
        data = {}
        store = SESSION.get_store(request.session)
        
        old_avatar = None
        if store.get("store_avatar"):
            old_avatar = store.store_avatar
            
        crop_coords = {
            "x1": int(request.POST["x1"]),
            "y1": int(request.POST["y1"]),
            "x2": int(request.POST["x2"]),
            "y2": int(request.POST["y2"]),
        }
        
        avatar = StoreAvatarTmp.objects.filter(session_key=\
            request.session.session_key)
        if not avatar:
            raise Http404
            
        avatar = avatar[0]
        
        # save the session before a cloud call!
        request.session.save()
        res = create_png(avatar.avatar.path, crop_coords)
        
        # make sure that we have the latest session
        session = SessionStore(request.session.session_key)
        store = SESSION.get_store(session)
        if res and 'error' not in res:
            store.store_avatar = res.get('name')
            store.store_avatar_url = res.get('url')
            # delete the model and file since it's useless to keep
            avatar.avatar.delete()
            avatar.delete()
            session['has_store_avatar'] = True
            
        store.update()
        
        session["store"] = store
        request.session.update(session)
        
        # need to remove old file
        if old_avatar:
            delete_file(old_avatar, 'png')
        
        # flag the execution of avatarCropComplete js function
        data['success'] = True
    
        # update the session cache
        request.session['store'] = store
        return render(request, 'manage/avatar_crop.djhtml', data)
    
    
    
    
    
    
    
        

