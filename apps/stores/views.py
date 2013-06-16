from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.forms.models import inlineformset_factory
from datetime import datetime

from apps.stores.models import Store as dStore, Hours as dHours
from apps.stores.forms import StoreForm, StoreAvatarForm
from libs.repunch.rphours_util import HoursInterpreter

from parse.utils import delete_file, create_png
from parse.apps.stores.models import Store
from parse.auth.decorators import login_required

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
    account = request.session['account']
    
    HoursFormSet = inlineformset_factory(dStore, dHours, extra=0)
    
    # build the list of hours in proper format for saving to Parse
    hours, ind, key = [], 0, "hours-0-days"
    while ind < 7:
        days = request.POST.getlist(key)
        if days:
            # format time from 10:00:00 to 1000
            open_time = request.POST["hours-" + str(ind) +\
                        "-open"].replace(":", "").zfill(6)[:4]
            close_time = request.POST["hours-" + str(ind) +\
                        "-close"].replace(":", "").zfill(6)[:4]
            for day in days:
                hours.append({
                    "day":int(day)-1, # days are from 0 to 6
                    "open_time":open_time,
                    "close_time":close_time,
                })
        ind += 1
        key = "hours-" + str(ind) + "-days"
        
    # fake a store to construct HoursFormset
    dstore_inst = dStore()
            
    if request.method == 'POST': 
        formset = HoursFormSet(request.POST, prefix='hours',
            instance=dstore_inst) 
            
        form = StoreForm(request.POST)
        if form.is_valid(): 
            store = Store(**account.get("store").__dict__)
            store.update_locally(request.POST.dict(), False)
            store.set("hours", hours)
            store.update()

            # store no longer has email field. Email now exclusive to
            # Accounts (_User) class
            account.email = request.POST['email']
            account.update()

            account.store = store
            request.session['account'] = account
            data['success'] = "Store details have been saved."
    else:
        form = StoreForm(account.get("store").__dict__)
        form.data['email'] = account.get('email')
        # TODO
        formset = HoursFormSet(prefix='hours', 
                            instance=dstore_inst)

    data['form'] = form
    data['hours_formset'] = formset

    return render(request, 'manage/store_edit.djhtml', data)

@login_required
def hours_preview(request):
    store = request.session['account'].get('store')
    
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
    account = request.session['account']
    store = account.get('store')
    
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
            account.store = store
            request.session['account'] = account;
            
            data['success'] = True
    else:
        form = StoreAvatarForm();
    
    data['form'] = form
    data['url'] = reverse('store_avatar')
    return render(request, 'manage/avatar_upload.djhtml', data)
