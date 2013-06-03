from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.forms.models import inlineformset_factory

from apps.stores.models import Store, Hours
from apps.accounts.models import Account
from apps.stores.forms import StoreForm, StoreAvatarForm
from libs.repunch.rphours_util import HoursInterpreter

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
    
    # TODO replace Hours formset
    # HoursFormSet = inlineformset_factory(Store, Hours, extra=0)
    
    if request.method == 'POST': 
        # formset = HoursFormSet(request.POST, prefix='hours',
        # instance=account.store)
        form = StoreForm(request.POST)
        if form.is_valid():# and formset.is_valid(): 
            store = Store(**account.get("store").__dict__)
            store.update_locally(request.POST.dict(), False)
            store.update()
            
            # formset.save()            
            
            #always need to reload form for deleted fields
            # formset = HoursFormSet(prefix='hours', instance=store) 
            #reload the store and put it in the session

            account.store = store
            request.session['account'] = account
            data['success'] = "Store details have been saved."
    else:
        form = StoreForm(account.get("store").__dict__);
        # formset = HoursFormSet(prefix='hours',
        # instance=account.store)

    
    data['form'] = form
    # data['hours_formset'] = formset
    
    return render(request, 'manage/store_edit.djhtml', data)
    
@login_required
def hours_preview(request):
    store = request.session['account'].store
    
    HoursFormSet = inlineformset_factory(Store, Hours, extra=0)
    
    hours = []
    formset = HoursFormSet(request.GET, prefix='hours', instance=store)
    if formset.is_valid():
        for form in formset:
            if(not 'DELETE' in form.changed_data):
                hours.append(form.instance)
    
    return HttpResponse(HoursInterpreter(hours).readable(), content_type="text/html")
    
    
@login_required
def avatar(request):
    data = {}
    account = request.session['account']
    store = account.get('store')
    
    if request.method == 'POST': 
        form = StoreAvatarForm(request.POST)
        print dir(request.FILES.dict()['store_avatar'].file)
        from PIL import Image
        im = Image.open(request.FILES.dict()['store_avatar'].file)
        im.save('tst.png', 'PNG')
        if form.is_valid():
            
            #need to remove old file]
            if store.store_avatar:
                try:                
                    store.store_avatar.delete()
                except Exception:
                    pass # do nothing, 
                
            store = super(StoreAvatarForm, self).save()
            if store != None:
                rputils.rescale(os.path.join(settings.MEDIA_ROOT, store.store_avatar.name))
            
            return store
            
            account.store = store;
            request.session['account'] = account;
            
            data['success'] = True
    else:
        form = StoreAvatarForm();
    
    data['form'] = form
    data['url'] = reverse('store_avatar')
    return render(request, 'manage/avatar_upload.djhtml', data)
