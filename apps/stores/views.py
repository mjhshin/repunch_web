"""
Views for the My Store and Settings tab in the dashboard.
"""
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

from apps.comet.models import CometSession
from apps.stores.models import UploadedImageFile, StoreActivate,\
UploadedAndCreatedImageFile
from apps.stores.forms import StoreForm, StoreLocationForm,\
SettingsForm, UploadImageForm
from libs.repunch.rphours_util import HoursInterpreter
from libs.repunch.rputils import get_timezone, get_map_data

from repunch.settings import MEDIA_ROOT, TIME_ZONE,\
COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY, IMAGE_THUMBNAIL_SIZE,\
IMAGE_THUMBNAIL_ASPECT_RATIO, IMAGE_COVER_MAX_EDGE
from parse.apps.patrons.models import Patron
from parse import session as SESSION
from parse.comet import comet_receive
from parse.decorators import access_required, admin_only
from parse.utils import delete_file, create_png
from parse.apps.stores.models import Store, StoreLocation, Settings
from parse.apps.stores import format_phone_number
from parse.auth.decorators import login_required, dev_login_required

@dev_login_required
@login_required
@access_required
def index(request):
    """
    Render the store details template.
    """
    data = {'account_nav': True}
    
    # inserting this success and error message into the template
    # should be done in a cleaner way - this was done by the first guy
    # I just didn't bother changing it.
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
        
    return render(request, 'manage/store_details.djhtml', data)

@dev_login_required
@login_required
@access_required
def set_active_location(request):
    """
    Sets the active store location id in the session.
    This is used when selecting a store location in the header nav
    or the tab nav.
    """
    store_location_id = request.GET.get("store_location_id")
    success = False
    if store_location_id in SESSION.get_store_locations(\
        request.session).keys():
        SESSION.set_active_store_location_id(request.session,
            store_location_id)
        success = True
        
        # trigger the comet response for other tabs.
        for comet in CometSession.objects.filter(\
            session_key=request.session.session_key):
            comet.modified = True
            comet.save()
        
    return HttpResponse(json.dumps({"success": success}),
        content_type="application/json")

@dev_login_required
@login_required
@admin_only(reverse_url="store_index")
def edit_store(request):
    """
    Render the edit store template or handle a form submission from it.
    """
    data = {'account_nav': True}
    store = SESSION.get_store(request.session)
    
    # validate form submission and redirect to store details if
    # success or re-render the store edit template with previous form
    # input and errors.
    if request.method == "POST":
        store_form = StoreForm(request.POST)
        
        if store_form.is_valid():
            store.update_locally(request.POST.dict(), False)
            store.update()
            
            # notify other dashboards
            comet_receive(store.objectId, {
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedStore": store.jsonify(),
            })

            # make sure that we have the latest session
            request.session.clear()
            request.session.update(SessionStore(request.session.session_key))
            
            return redirect(reverse('store_index')+ "?%s" %\
                urllib.urlencode({'success': 'Store details has been updated.'}))
        
    # user navigates to this page so just render the store edit template
    # with a blank form.
    else:
        store_form = StoreForm()
        store_form.initial = store.__dict__.copy()
        
    data['store_form'] = store_form 
    
    return render(request, 'manage/store_edit.html', data)

@dev_login_required
@login_required
@admin_only(reverse_url="store_index")
def edit_location(request, store_location_id):
    """
    Renders the edit location template or handle form submissions
    for location creation or update.
    """
    data = {'account_nav': True, 'store_location_id': store_location_id}
    store = SESSION.get_store(request.session)
    
    # we are editing a new location if store_location_id is 0
    new_location = store_location_id == '0'
        
    def common(store_location_form):
        """
        Returns a rendered store location edit template with the given
        store location form.
        """
        data['store_location_form'] = store_location_form
        return render(request, 'manage/store_location_edit.djhtml', data)
            
    # Handle form submission and return the appropriate json response
    if request.method == 'POST': 
        store_location_form = StoreLocationForm(request.POST)
        
        postDict = request.POST.dict()
        hours = HoursInterpreter(json.loads(postDict["hours"]))
        
        # we are either creating a new store location or updating an
        # existing one with new values in the postDict
        if new_location:
            store_location = StoreLocation(**postDict)
        else:
            store_location = SESSION.get_store_location(\
                request.session, store_location_id)
            store_location.update_locally(postDict, False)
            
        if store_location_form.is_valid(): 
            # validate and format the hours
            hours_validation = hours.is_valid()
            if type(hours_validation) is bool:
                store_location.set("hours", hours.from_javascript_to_parse())
            else:
                data['hours_data'] = hours._format_javascript_input()
                data['hours_error'] = hours_validation
                return HttpResponse(json.dumps({
                    "result": "error",
                    "html": common(store_location_form).content,
                }), content_type="application/json")
            
            # set the timezone
            if store_location.get('zip'):
                store_location.store_timezone =\
                    get_timezone(store_location.get('zip')).zone
                    
            # format the phone number
            store_location.phone_number =\
                format_phone_number(postDict['phone_number'])
            # update the store's coordinates and neighborhood
            full_address = " ".join(\
                store_location.get_full_address().split(", "))
            map_data = get_map_data(full_address)
            store_location.set("coordinates", map_data.get("coordinates"))
            store_location.set("neighborhood", 
                store_location.get_best_fit_neighborhood(\
                    map_data.get("neighborhood")))
           
            if new_location:
                store_location.Store = store.objectId  
                store_location.create()
                store.array_add_unique("store_locations", [store_location])

            else:  
                store_location.update()
                # if this location is the first location then update 
                # the corresponding store columns for backwards compat
                sl_list = SESSION.get_store_locations_list(request.session)
                if sl_list[0].objectId == store_location.objectId:
                    store.inherit_store_location(store_location)
                    store.update()
            
            payload = {
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                "updatedStore": store.jsonify(),
                "updatedStoreLocation": store_location.jsonify(),
            }
            comet_receive(store.objectId, payload)
            
            # make sure that we have the latest session
            request.session.clear()
            request.session.update(SessionStore(request.session.session_key))
            
            if new_location:
                success_msg = 'New store location has been added.'
            else:
                success_msg = 'Store location has been updated.'
                
            # set the active location to this one
            SESSION.set_active_store_location_id(request.session,
                store_location.objectId)
            
            return HttpResponse(json.dumps({
                "result": "success",
                "url": reverse('store_index')+ "?%s" %\
                    urllib.urlencode({'success': success_msg})
            }), content_type="application/json")
            
            
        else:
            data['store_location'] = store_location
            data['hours_data'] = hours._format_javascript_input()
            
            return HttpResponse(json.dumps({
                "result": "error",
                "html": common(store_location_form).content,
            }), content_type="application/json")
       
    # user navigated to this page so just render a store location edit
    # template with a blank form (if new_location) or a form with fields
    # filled out if user is editing an existing location    
    else:
        store_location_form = StoreLocationForm(None)
        
        # user is editing an existing location so fill up initial
        # form content
        if not new_location:
            store_location = SESSION.get_store_location(\
                request.session, store_location_id)
            store_location_form.initial = store_location.__dict__.copy()
            # make sure that the phone number is unformatted
            store_location_form.initial['phone_number'] =\
                store_location_form.initial['phone_number'].replace("(",
                    "").replace(")","").replace(" ", "").replace("-","")
                    
            data['store_location'] = store_location
            data['hours_data'] = HoursInterpreter(\
                store_location.hours)._format_parse_input()
         
    return common(store_location_form)


@dev_login_required
@login_required
@access_required(http_response="Access denied", content_type="text/plain")
@csrf_exempt
def hours_preview(request):
    """
    Returns a json response containing the readable hours in html
    given a properly formatted POST data. The format of the POST
    data is specified in the HoursInterpreter.
    
    If the hours in the POST data produces an incorrect hours 
    (overlapping hours or close time lexicographically less than open
    time, etc).
    """
    if request.method != "POST":
        return "Bad request"

    hours = HoursInterpreter(request.POST)
    hours_validation = hours.is_valid()
    if type(hours_validation) is bool:
        result = "success"
        html = HoursInterpreter(request.POST).from_javascript_to_readable()
    else:
        result = "error"
        html = hours_validation
    
    return HttpResponse(json.dumps({
        "result": result,
        "html": html,
    }), content_type="application/json")


@login_required
@dev_login_required
@access_required(http_response="<h1>Access denied</h1>",\
content_type="text/html")
@csrf_exempt
def image_upload(request):
    """
    Renders the image upload template for GET requests or POST requests
    with form errors.
    """
    
    # user submitted an image form which we validate
    # if the form is valid the we render the image crop template
    # else we render the image upload template with previous form 
    # input and errors
    if request.method == 'POST': 
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
        
            # save the file locallly
            image = form.save(request.session.session_key)
            
            # height is limiting
            if image.width > image.height: 
                center_width = image.width * 0.5
                init_y1 = image.height * 0.125
                init_y2 = image.height * 0.875
                length = init_y2 - init_y1
                init_x1 = center_width - length / 2
                init_x2 = center_width + length / 2
            else:
                center_height = image.height * 0.5
                init_x1 = image.width * 0.125
                init_x2 = image.width * 0.875
                length = init_x2 - init_x1
                init_y1 = center_height - length / 2
                init_y2 = center_height + length / 2
                
                
            return render(request, 'manage/image_crop.djhtml', {
                'image': image,
                'init_x1': init_x1,
                'init_y1': init_y1,
                'init_x2': init_x2,
                'init_y2': init_y2,
                'aspect_ratio': IMAGE_THUMBNAIL_ASPECT_RATIO, 
            })
            
    # user navigated to this page so just render the image upload
    # template with a blank form.
    else:
        form = UploadImageForm()
    
    return render(request, 'manage/image_upload.djhtml', {
        'form': form,
        'url': reverse('store_image_upload')
    })
    
@dev_login_required
@login_required
@access_required(http_response="<h1>Access denied</h1>",\
content_type="text/html")
def image_get(request):
    """
    Returns a json response containing the cover and thumbnail url
    for the store.
    """
    if request.method == "GET":
        store = SESSION.get_store(request.session)
        return HttpResponse(json.dumps({
            "src_cover": store.cover_image_url,
            "src_thumbnail": store.thumbnail_image_url,
        }), content_type="application/json")
        
    raise Http404
    
@dev_login_required
@login_required
@admin_only(http_response="<h1>Permission denied</h1>",\
content_type="text/html")
@csrf_exempt
def image_crop(request):
    """
    Takes in crop coordinates and creates a new png image.
    """
    if request.method == "POST":
        data = {}
        store = SESSION.get_store(request.session)
        
        old_cover, old_thumbnail = None, None
        if store.get("cover_image"):
            old_cover = store.get("cover_image")
        if store.get("thumbnail_image"):
            old_thumbnail = store.get("thumbnail_image")
            
        # if there are 2 windows with the same session_key editing the 
        # store image, the image will be deleted by the first window
        # to crop. The 2nd window will then have no image.
        image = UploadedImageFile.objects.filter(session_key=\
            request.session.session_key)
            
        if not image:
            # flag the execution of image Crop Complete js function
            data['success'] = True
            return render(request, 'manage/image_crop.djhtml', data)
            
        image = image[0]
        
        # the crop coords are used for the thumbnail_image
        crop_coords = None
        if len(request.POST["x1"]) > 0:
            crop_coords = {
                "x1": int(request.POST["x1"].split(".")[0]),
                "y1": int(request.POST["y1"].split(".")[0]),
                "x2": int(request.POST["x2"].split(".")[0]),
                "y2": int(request.POST["y2"].split(".")[0]),
            }
        
        # save the session before a cloud call!
        request.session.save()
        
        res_cover = create_png(image.image.path)
        res_thumbnail = create_png(image.image.path,
            IMAGE_THUMBNAIL_SIZE, crop_coords)
        
        # make sure that we have the latest session
        session = SessionStore(request.session.session_key)
        store = SESSION.get_store(session)
        
        if res_cover and 'error' not in res_cover:
            setattr(store, "cover_image", res_cover.get('name'))
            setattr(store, "cover_image_url", res_cover.get('url').replace(\
                "http:/", "https://s3.amazonaws.com"))
        
        if res_thumbnail and 'error' not in res_thumbnail:
            setattr(store, "thumbnail_image", res_thumbnail.get('name'))
            setattr(store, "thumbnail_image_url", res_thumbnail.get('url').replace(\
                "http:/", "https://s3.amazonaws.com"))
                
            # below here for backwards compat
            store.store_avatar = getattr(store, "thumbnail_image")
            store.store_avatar_url = getattr(store, "thumbnail_image_url")
            store.update()
                
        # delete the model and file since it's useless to keep
        image.delete()
        
        # notify other dashboards of this change
        payload = {
            COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
            "updatedStoreThumbnailName": store.thumbnail_image,
            "updatedStoreThumbnailUrl": store.thumbnail_image_url,
            "updatedStoreCoverName": store.cover_image,
            "updatedStoreCoverUrl": store.cover_image_url,
        }
        
        comet_receive(store.objectId, payload)
        
        # need to remove old files
        if old_cover:
            delete_file(old_cover, 'image/png')
            
        if old_thumbnail:
            delete_file(old_thumbnail, 'image/png')
        
        # flag the execution of image Crop Complete js function
        data['success'] = True
    
        # make sure we have latest session data
        request.session.clear()
        request.session.update(SessionStore(request.session.session_key))
        
        return render(request, 'manage/image_crop.djhtml', data)
    
    raise Http404
    

@dev_login_required
@login_required
@admin_only(except_method="GET")
def settings(request):
    """
    Renders the settings page or handles changes to it.
    """
    data = {'settings_nav': True}
    store = SESSION.get_store(request.session)
    settings = SESSION.get_settings(request.session)
    
    # user made changes
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
            data['error'] = 'Error saving settings.'
            
    # user navigated to this page so just render the settings template
    # with a filled settings form
    else:
        form = SettingsForm()
        form.initial = settings.__dict__.copy()
        # shin chose to move punches_facebook to Store...
        form.initial['punches_facebook'] =\
            store.get('punches_facebook')
    
    # update the session cache since we may have made changes above
    request.session['store'] = store
    request.session['settings'] = settings
    
    data['form'] = form
    data['settings'] = settings
    return render(request, 'manage/settings.djhtml', data)

@dev_login_required
@login_required
@admin_only(http_response={"error": "Permission denied"})
def refresh(request):
    """
    Returns a json response containing a new retailer_pin for the store.
    """
    
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
    
    
        

