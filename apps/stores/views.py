from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.forms.models import inlineformset_factory
from datetime import datetime

from apps.stores.forms import StoreForm, StoreAvatarForm
from libs.repunch.rphours_util import HoursInterpreter

from parse.utils import delete_file, create_png
from parse.apps.stores.models import Store, Hours
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
    
    if request.method == 'POST': 
        form = StoreForm(request.POST)
        if form.is_valid(): 
            store = Store(**account.get("store").__dict__)
            store.update_locally(request.POST.dict(), False)
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

    
    data['form'] = form

    return render(request, 'manage/store_edit.djhtml', data)

@login_required
def hours_preview(request):
    store = request.session['account'].get('store')
    
    for key, value in request.GET.dict().iteritems():
        print key, value # TODO

    return HttpResponse(HoursInterpreter([ Hours(days=["1","2","3"], open=datetime.now(), close=datetime.now(), list_order=1) ]).readable(), content_type="text/html")
    
    
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
