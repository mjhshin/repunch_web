from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
import urllib

from apps.rewards.models import Reward
from apps.rewards.forms import RewardForm, RewardAvatarForm

@login_required
def index(request):
    data = {'rewards_nav': True}
    store = request.session['account'].store
    
    data['rewards'] = Reward.objects.filter(store=store.id).order_by('punches')
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/rewards.djhtml', data)


@login_required
def edit(request, reward_id):
    reward_id = int(reward_id)
    reward = None
    store = request.session['account'].store
    data = {'rewards_nav': True, 'reward_id': reward_id}
    data['is_new'] = (reward_id==0);
    
    #need to make sure this reward really belongs to this store
    if(reward_id > 0):
        try:
            reward = Reward.objects.filter(store=store.id).get(id=reward_id)
        except Reward.DoesNotExist:
            raise Http404
    
    if request.method == 'POST': # If the form has been submitted...
        form = RewardForm(request.POST, instance=reward) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            reward = form.save(commit=False)
            reward.store = store
            reward.save();
            #reload the store and put it in the session
            if reward_id > 0:
                data['success'] = "Reward has been updated."
            else:
                return HttpResponseRedirect(reward.get_absolute_url()+ "?%s" % urllib.urlencode({'success': 'Reward has been added.'}))#Since this is new we need to redirect the page
    else:
        if reward_id == 0:
            form = RewardForm()
        else:
            if request.GET.get("success"):
                data['success'] = request.GET.get("success")
            if request.GET.get("error"):
                data['error'] = request.GET.get("error")
            
            form = RewardForm(instance=reward)
    
    data['form'] = form
    return render(request, 'manage/reward_edit.djhtml', data)

@login_required
def delete(request, reward_id):
    reward_id = int(reward_id)
    reward = None
    store = request.session['account'].store
    
    #need to make sure this reward really belongs to this store
    if(reward_id > 0):
        try:
            reward = Reward.objects.filter(store=store.id).get(id=reward_id)
        except Reward.DoesNotExist:
            raise Http404
    else:
        raise Http404
    
    reward.delete()
    return redirect(reverse('rewards_index')+ "?%s" % urllib.urlencode({'success': 'Reward has been removed.'}))

@login_required
def avatar(request, reward_id):
    reward_id = int(reward_id)
    data = {}
    store = request.session['account'].store
    
    #need to make sure this reward really belongs to this store
    if(reward_id > 0):
        try:
            reward = Reward.objects.filter(store=store.id).get(id=reward_id)
        except Reward.DoesNotExist:
            raise Http404
    else:
        raise Http404
    
    if request.method == 'POST': # If the form has been submitted...
        form = RewardAvatarForm(request.POST, request.FILES, instance=reward) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            form.save()
            data['success'] = True
    else:
        form = RewardAvatarForm();
    
    data['form'] = form
    data['url'] = reverse('reward_avatar', args=[reward_id])
    return render(request, 'manage/avatar_upload.djhtml', data)
