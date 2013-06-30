from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
import urllib

from parse.decorators import session_comet
from parse import session as SESSION
from parse.auth.decorators import login_required
from apps.rewards.forms import RewardForm, RewardAvatarForm

@login_required
@session_comet
def index(request):
    data = {'rewards_nav': True}
    store = SESSION.get_store(request.session)
    lst, rewards = [], store.get('rewards')
    # create a reward map
    if rewards:
        # record the pre-sorted reward
        presorted = [(reward['reward_id'], 
            int(reward['punches'])) for reward in rewards]
        # cannot just use punches as the map since it is not unique
        reward_map = {(reward['reward_id'], 
            int(reward['punches'])):reward for reward in rewards}
        # get a sorted list of punches in descending order
        sorted_ = presorted[:]
        sorted_.sort(key=lambda r: r[1])
        
        sorted_rewards = [reward_map[p] for p in sorted_]
        store.rewards = sorted_rewards
        
        # do not just update needlessly check if order has changed.
        for i, pre in enumerate(presorted):
            if pre[0] != sorted_[i][0]:
                store.update()
        
        data['rewards'] = sorted_rewards
    else:
        data['rewards'] = []
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
        
    # update session cache
    request.session['store'] = store
    
    return render(request, 'manage/rewards.djhtml', data)


@login_required
@session_comet
def edit(request, reward_index):
    data = {'rewards_nav': True}
    store = SESSION.get_store(request.session)
    rewards = store.get('rewards')
    if rewards:
        init_count = len(rewards)
    else:
        init_count = 0

    try:
        reward_index = int(reward_index)
    except ValueError:
        raise Http404
 
    # reward id being -1 is a flag for new reward which don't exist
    is_new, reward = False, None
    if reward_index < init_count and reward_index > -2:
        if reward_index == -1:
            is_new = True
            # a reward is now just a dictionary to be added to 
            # the rewards array
            reward = {'reward_name':None, "description":None, 
                        "punches":None, 'redemption_count':0}
        else: # reward exists
            old_reward = rewards[reward_index]
    else: 
        raise Http404
    
    if request.method == 'POST': 
        form = RewardForm(request.POST) 
        if form.is_valid():
            reward = {'reward_name':form.data['reward_name'], 
                "description":form.data['description'], 
                "punches":form.data['punches'],
                "redemption_count":0}
                
            # assign a new reward_id
            ids, msg = [], ""
            for r in rewards:
                ids.append(r.get("reward_id"))
            ids.sort()           
  
            if not is_new:
                msg = 'Reward has been updated.'
                reward["redemption_count"] =\
                    old_reward["redemption_count"]
                reward['reward_id'] = old_reward['reward_id']
                store.array_remove('rewards', [old_reward])
            elif len(ids) == 0:
                msg = 'Reward has been added.'
                reward['reward_id'] = 0
            else:
                msg = 'Reward has been added.'
                reward['reward_id'] = ids[-1] + 1
            
            store.array_add_unique('rewards', [reward])
            store.rewards = None
            
            # update session cache
            request.session['store'] = store
            
            return redirect(reverse('rewards_index')+\
                "?%s" % urllib.urlencode({'success':msg}))
    else:
        if reward_index >= 0 :
            form = RewardForm(rewards[reward_index])
        else:
            form = RewardForm()
        if not is_new:
            if request.GET.get("success"):
                data['success'] = request.GET.get("success")
            if request.GET.get("error"):
                data['error'] = request.GET.get("error")
                
    # update session cache
    request.session['store'] = store

    data['is_new'] = is_new;
    data['reward'] = reward
    data['reward_index'] = reward_index
    data['form'] = form
    return render(request, 'manage/reward_edit.djhtml', data)

@login_required
@session_comet
def delete(request, reward_index):
    account = request.session['account']
    store = SESSION.get_store(request.session)
    rewards = store.get('rewards')

    try:
        reward_index = int(reward_index)
    except ValueError:
        raise Http404
    
    #need to make sure this reward really belongs to this store
    reward = rewards[reward_index]
    if not reward:
        raise Http404
    
    store.array_remove('rewards', [reward])
    store.rewards = None
    store.get('rewards')
    
    # update session cache
    request.session['store'] = store
    
    return redirect(reverse('rewards_index')+\
                "?%s" % urllib.urlencode({'success':\
                'Reward has been removed.'}))


@login_required
def avatar(request, reward_index):
    """
    Unused at the moment
    """
    raise  Http404
