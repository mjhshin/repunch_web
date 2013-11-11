from django.shortcuts import render, redirect
from django.contrib.auth import SESSION_KEY
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.backends.cache import SessionStore
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http.request import QueryDict
from datetime import datetime
from io import BytesIO
import json, urllib, urllib2, os, pytz

from apps.stores.models import StoreAvatarTmp, StoreActivate
from apps.stores.forms import StoreForm, SettingsForm, StoreAvatarForm
from libs.repunch.rphours_util import HoursInterpreter
from libs.repunch.rputils import get_timezone, get_map_data

from repunch.settings import MEDIA_ROOT, TIME_ZONE,\
COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY
from parse.apps.patrons.models import Patron
from parse import session as SESSION
from parse.comet import comet_receive
from parse.decorators import access_required, admin_only
from parse.utils import delete_file, create_png
from parse.apps.stores.models import Store, Settings
from parse.apps.stores import format_phone_number
from parse.auth.decorators import login_required, dev_login_required

@dev_login_required
@login_required
@access_required
def index(request):
    data = {'account_nav': True}
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/store_details.djhtml', data)

@dev_login_required
@login_required
@admin_only(reverse_url="store_index")
def edit(request):
    store = SESSION.get_store(request.session)
    data = {'account_nav': True}
    
    def common(form):
        # TODO
        # update the session cache
        request.session['store'] = store
        data['form'] = form

        return render(request, 'manage/store_edit.djhtml', data)
            
    if request.method == 'POST': 
        form = StoreForm(request.POST)
            
        if form.is_valid(): 
            store = Store(**store.__dict__)
            store.update_locally(request.POST.dict(), False)
            # store.set("hours", hours)
            
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
            try:
                request.session['store_timezone'] =\
                    pytz.timezone(store.store_timezone)
            except Exception:
                request.session['store_timezone'] =\
                    pytz.timezone(TIME_ZONE)
                
            request.session['store'] = store
            
            # notify other dashboards of this change
            payload = {
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedStore": store.jsonify(),
            }
            comet_receive(store.objectId, payload)
            
            return redirect(reverse('store_index')+ "?%s" %\
                        urllib.urlencode({'success':\
                            'Store details has been updated.'}))
                
    else:
        form = StoreForm(None)
        form.initial = store.__dict__.copy()
        # make sure that the phone number is unformatted
        form.initial['phone_number'] =\
            form.initial['phone_number'].replace("(",
                "").replace(")","").replace(" ", "").replace("-","")
         
    return common(form)

# this accessed only through the edit_store detail page, which
# requires admin access but this might be useful somewhere else
# so the admin_only decorator is not used
@dev_login_required
@login_required
@access_required(http_response="Access denied", content_type="text/plain")
def hours_preview(request):
    print request.POST
    return HttpResponse(HoursInterpreter(request.POST).readable(), 
                        content_type="text/html")
    
    
@login_required
@dev_login_required
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
    
@dev_login_required
@login_required
@access_required(http_response="<h1>Access denied</h1>",\
content_type="text/html")
def get_avatar(request):
    """ returns the store's avatar url """
    if request.method == "GET":
        store = SESSION.get_store(request.session)
        return HttpResponse(store.get("store_avatar_url"))
        
    raise Http404

@dev_login_required
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
        request.session.clear()
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
    

@dev_login_required
@login_required
@admin_only(except_method="GET")
def settings(request):
    data = {'settings_nav': True}
    store = SESSION.get_store(request.session)
    settings = SESSION.get_settings(request.session)
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid(): 
            # expect numbers so cast to int
            dct = request.POST.dict().copy()
            dct['punches_employee'] = int(dct['punches_employee'])
            settings.update_locally(dct, False)
            settings.update()
            # Shin chose to move punches_facebook to Store...
            store.set("punches_facebook", 
                        int(request.POST["punches_facebook"]))
            store.Settings = settings.objectId
            store.settings = settings
            store.update()
            
            # notify other dashboards of this changes
            payload = {
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedSettings":settings.jsonify(),
                "updatedPunchesFacebook_int":\
                    store.punches_facebook,
            }
            comet_receive(store.objectId, payload)

            data['success'] = "Settings have been saved."
        else:
            data['error'] = 'Error saving settings.';
    else:
        form = SettingsForm()
        form.initial = settings.__dict__.copy()
        # shin chose to move punches_facebook to Store...
        form.initial['punches_facebook'] =\
            store.get('punches_facebook')
    
    # update the session cache
    request.session['store'] = store
    request.session['settings'] = settings
    
    data['form'] = form
    data['settings'] = settings
    return render(request, 'manage/settings.djhtml', data)

@dev_login_required
@login_required
@admin_only(http_response={"error": "Permission denied"})
def refresh(request):
    if request.session.get('account') and\
            request.session.get(SESSION_KEY):
        data = {'success': False}
        settings = SESSION.get_settings(request.session)
        
        if settings == None:
            raise Http404
        else:
            settings.set('retailer_pin', Settings.generate_id())
            settings.update()
            
            # update the session cache
            request.session['settings'] = settings
            
            # notify other dashboards of these changes
            store = SESSION.get_store(request.session)
            payload = {
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedSettings":settings.jsonify()
            }
            comet_receive(store.objectId, payload)
            
            data['success'] = True
            data['retailer_pin'] = settings.retailer_pin
        
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'success': False}), content_type="application/json")

@csrf_exempt
def activate(request):
    """
    Handles account activation from email form sent at user sign up.
    """
    if request.method == "POST":
        store_id = request.POST['store_id']
        act_id = request.POST['act_id']
        act = StoreActivate.objects.filter(id=act_id,
                store_id=store_id)
        if len(act) > 0:
            act[0].delete()
            store = Store.objects().get(objectId=store_id)
            if store:
                store.active = True
                store.update()
                return HttpResponse(store.get(\
                    "store_name").capitalize() +\
                    " has been activated.")
            else:
                return HttpResponse("Account/store not found.")  
        else:  
            return HttpResponse("This form has already "+\
                "been used.")                
    
    return HttpResponse("Bad request")
    
@dev_login_required
@login_required
@admin_only(reverse_url="store_index")
def deactivate(request):
    """
    This does not delete anything! It merely sets the store's active
    field to false and logs the user out.
    """
    store = request.session['store']
    store.active = False
    store.update()
    # notify other dashboards of this changes
    payload = {
        COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
        "updatedStore":store.jsonify(),
    }
    comet_receive(store.objectId, payload)
    return redirect(reverse('manage_logout'))
    
    
        

