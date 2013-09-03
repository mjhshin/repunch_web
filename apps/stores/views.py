from django.shortcuts import render, redirect
from django.contrib.auth import SESSION_KEY
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.backends.cache import SessionStore
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http.request import QueryDict
from django.forms.models import inlineformset_factory
from datetime import datetime
from io import BytesIO
import json, urllib, urllib2, os, pytz

from apps.stores.models import Store as dStore, Hours as dHours,\
StoreAvatarTmp
from apps.stores.forms import StoreForm, StoreAvatarForm
from libs.repunch.rphours_util import HoursInterpreter
from libs.repunch.rputils import get_timezone, get_map_data

from repunch.settings import MEDIA_ROOT, TIME_ZONE,\
COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY
from parse.apps.patrons.models import Patron
from parse import session as SESSION
from parse.comet import comet_receive
from parse.decorators import access_required, admin_only
from parse.utils import delete_file, create_png
from parse.apps.stores.models import Store
from parse.apps.stores import format_phone_number
from parse.auth.decorators import login_required

@login_required
@access_required
def index(request):
    data = {'account_nav': True}
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/store_details.djhtml', data)

@login_required
@admin_only(reverse_url="store_index")
def edit(request):
    account = request.session['account']
    store = SESSION.get_store(request.session)
    
    data = {'account_nav': True}
    # fake a store to construct HoursFormset - probably not necessary
    dstore_inst = dStore()
    
    def common(form):
        hours_map = {}
        # group up the days that are in the same row
        if store.get("hours"):
            for hour in store.get("hours"):
                key = (hour['close_time'], hour['open_time'])
                if key in hours_map:
                    hours_map[key].append(hour['day'])
                else:
                    hours_map[key] = [hour['day']]
                
        # create the formset
        HoursFormSet = inlineformset_factory(dStore, dHours,
                            max_num=7, extra=len(hours_map))
        formset = HoursFormSet(prefix='hours', instance=dstore_inst)
        hrsmap_vk, days_list = {}, []
        for k, v in hours_map.iteritems():
            v.sort()
            v_tup = tuple(v)
            hrsmap_vk[v_tup] = k
            days_list.append(v_tup)
        # now sort the days list by first element
        days_list.sort(key=lambda k: k[0])
        
        # set forms in formset initial data
        for i, days in enumerate(days_list):
            d = {'days':[unicode(d) for d in days],
                    'open':unicode(hrsmap_vk[days][1][:2] +\
                            ':' + hrsmap_vk[days][1][2:4] + ':00'),
                    'close':unicode( hrsmap_vk[days][0][:2] +\
                            ':' +  hrsmap_vk[days][0][2:4] + ':00'),
                    'list_order':unicode(i+1) }
            formset[i].initial = d
                
        # update the session cache
        request.session['account'] = account
        request.session['store'] = store
           
        data['form'] = form
        data['hours_formset'] = formset

        return render(request, 'manage/store_edit.djhtml', data)
            
    if request.method == 'POST': 
        HoursFormSet = inlineformset_factory(dStore, dHours,
                            max_num=7, extra=0)
        formset = HoursFormSet(request.POST, prefix='hours',
                                instance=dstore_inst) 
        form = StoreForm(account.email, request.POST)
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
            # sort the list
            hours.sort(key=lambda k: k['day'])
            
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
            
            # update the account - email = username!
            account.email = request.POST['email']
            account.username = request.POST['email']
            account.update()
            
            # update the session cache
            try:
                request.session['store_timezone'] =\
                    pytz.timezone(store.store_timezone)
            except Exception:
                request.session['store_timezone'] =\
                    pytz.timezone(TIME_ZONE)
                
            request.session['account'] = account
            request.session['store'] = store
            
            # notify other dashboards of this change
            payload = {
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedStore": store.jsonify(),
                "updatedAccount": account.jsonify()
            }
            comet_receive(store.objectId, payload)
            
            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Store details has been updated.'}))
                
    else:
        form = StoreForm(None)
        form.initial = store.__dict__.copy()
        # the email is in the account
        form.initial['email'] = account.email
        # make sure that the phone number is unformatted
        form.initial['phone_number'] =\
            form.initial['phone_number'].replace("(",
                "").replace(")","").replace(" ", "").replace("-","")
         
    return common(form)

# this accessed only through the edit_store detail page, which
# requires admin access but this might be useful somewhere else
# so the admin_only decorator is not used
@login_required
@access_required(http_response="Access denied", content_type="text/plain")
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
@access_required(http_response="<h1>Access denied</h1>",\
content_type="text/html")
@csrf_exempt
def avatar(request):
    data = {}
    store = SESSION.get_store(request.session)
    
    if request.method == 'POST': 
        form = StoreAvatarForm(request.POST, request.FILES)
        if form.is_valid():
        
            # save the file locallly
            avatar = form.save(request.session.session_key)
            
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
    
# TODO http_response on access_required should be a link to an image
@login_required
@access_required(http_response="<h1>Access denied</h1>",\
content_type="text/html")
def get_avatar(request):
    """ returns the store's avatar url """
    if request.method == "GET" or request.is_ajax():
        store = SESSION.get_store(request.session)
        return HttpResponse(store.get("store_avatar_url"))
        
    raise Http404

@login_required
@admin_only(http_response="<h1>Permission denied</h1>",\
content_type="text/html")
@csrf_exempt
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
        # if there are 2 windows with the same session_key editing the 
        # store avatar, the avatar will be deleted by the first window
        # to crop. The 2nd window will then have no avatar.
        if not avatar:
            # flag the execution of avatarCropComplete js function
            data['success'] = True
            return render(request, 'manage/avatar_crop.djhtml', data)
            
        avatar = avatar[0]
        
        # save the session before a cloud call!
        request.session.save()
        res = create_png(avatar.avatar.path, crop_coords)
        
        # make sure that we have the latest session
        session = SessionStore(request.session.session_key)
        store = SESSION.get_store(session)
        if res and 'error' not in res:
            store.store_avatar = res.get('name')
            store.store_avatar_url =\
                res.get('url').replace("http:/",
                    "https://s3.amazonaws.com")
            # delete the model and file since it's useless to keep
            avatar.avatar.delete()
            avatar.delete()
            session['has_store_avatar'] = True
            
        store.update()
        
        session["store"] = store
        request.session.update(session)
        
        # notify other dashboards of this change
        payload = {
            COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
            "updatedStoreAvatarName_str":store.store_avatar,
            "updatedStoreAvatarUrl_str":store.store_avatar_url, 
        }
        comet_receive(store.objectId, payload)
        
        # need to remove old file
        if old_avatar:
            delete_file(old_avatar, 'image/png')
        
        # flag the execution of avatarCropComplete js function
        data['success'] = True
    
        # update the session cache
        request.session['store'] = store
        return render(request, 'manage/avatar_crop.djhtml', data)
    
    raise Http404
    
    
    
    
    
        

