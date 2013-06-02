from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.forms.models import inlineformset_factory

from apps.stores.models import Store, Hours
from apps.accounts.models import Account
from apps.stores.forms import StoreForm, StoreAvatarForm
from libs.repunch.rphours_util import HoursInterpreter
from parse.auth.decorators import login_required

from parse.apps.stores.forms import StoreForm as pStoreForm

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
    
    if request.method == 'POST': # If the form has been submitted...
        # formset = HoursFormSet(request.POST, prefix='hours', instance=account.store)
        form = StoreForm(request.POST) # A form bound to the POST data
        pform = pStoreForm(instance=account.get("store"), 
                            **request.POST.dict())
        
        if pform.is_valid(form.errors):# and formset.is_valid(): # All validation rules pass
            pform.update()
            
            # formset.save()            
            
            #always need to reload form for deleted fields
            # formset = HoursFormSet(prefix='hours', instance=store) 
            #reload the store and put it in the session

            account.store = pform.store
            data['success'] = "Store details have been saved."
    else:
        form = StoreForm(account.get("store").__dict__);
        # formset = HoursFormSet(prefix='hours', instance=account.store)

    
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
    
    if request.method == 'POST': # If the form has been submitted...
        form = StoreAvatarForm(request.POST, request.FILES, instance=account.store) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            
            #need to remove old file
            store = form.save()
            
            #resize image if
            
            account.store = store;
            request.session['account'] = account;
            
            data['success'] = True
    else:
        form = StoreAvatarForm();
    
    data['form'] = form
    data['url'] = reverse('store_avatar')
    return render(request, 'manage/avatar_upload.djhtml', data)
