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
        reward_map = {int(reward['punches']):reward for reward in rewards}
        # get a sorted list of punches in descending order
        punches = [p for p in reward_map.iterkeys()]
        punches.sort()
        sorted_rewards = [reward_map[p] for p in punches]
        store.rewards = sorted_rewards
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
def edit(request, reward_id):
    data = {'rewards_nav': True}
    store = SESSION.get_store(request.session)
    rewards = store.get('rewards')
    if rewards:
        init_count = len(rewards)
    else:
        init_count = 0

    try:
        reward_id = int(reward_id)
    except ValueError:
        raise Http404
 
    # reward id being -1 is a flag for new reward which don't exist
    is_new, reward = False, None
    if reward_id < init_count and reward_id > -2:
        if reward_id == -1:
            is_new = True
            # a reward is now just a dictionary to be added to 
            # the rewards array
            reward = {'reward_name':None, "description":None, 
                        "punches":None, 'redemption_count':0}
        else: # reward exists
            old_reward = rewards[reward_id]
    else: 
        raise Http404
    
    if request.method == 'POST': 
        form = RewardForm(request.POST) 
        if form.is_valid():
            reward = {'reward_name':form.data['reward_name'], 
                "description":form.data['description'], 
                "punches":form.data['punches'],
                "redemption_count":0}
  
            if not is_new:
                reward["redemption_count"] =\
                    old_reward["redemption_count"]
                store.array_remove('rewards', [old_reward])

            store.array_add_unique('rewards', [reward])

            
            now_count = len(store.get('rewards'))
            if now_count > init_count:
                reward_id = now_count - 1
            
            data['reward_id'] = len(store.get('rewards'))
            data['success'] = "Reward has been updated."
            
            # update session cache
            request.session['store'] = store
            
            return redirect(reverse('rewards_index')+\
                "?%s" % urllib.urlencode({'success':\
                'Reward has been added.'}))
    else:
        if reward_id >= 0 :
            form = RewardForm(rewards[reward_id])
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
    data['reward_id'] = reward_id
    data['form'] = form
    return render(request, 'manage/reward_edit.djhtml', data)

@login_required
@session_comet
def delete(request, reward_id):
    account = request.session['account']
    store = SESSION.get_store(request.session)
    rewards = store.get('rewards')

    try:
        reward_id = int(reward_id)
    except ValueError:
        raise Http404
    
    #need to make sure this reward really belongs to this store
    reward = rewards[reward_id]
    if not reward:
        raise Http404
    
    store.array_remove('rewards', [reward])
    
    # update session cache
    request.session['store'] = store
    
    return redirect(reverse('rewards_index')+\
                "?%s" % urllib.urlencode({'success':\
                'Reward has been removed.'}))


@login_required
def avatar(request, reward_id):
    """
    Unused at the moment
    """
    """
    data = {}
    account = request.session['account']
    store = account.get('store')
    
    #need to make sure this reward really belongs to this store
    reward = Reward.objects().get(Store=\
                        store.objectId, objectId=reward_id)
    if not reward:
        raise Http404
    
    if request.method == 'POST':
        # request.FILES ?
        form = RewardAvatarForm(request.POST) 
        if form.is_valid():
            # TODO delete previous file
            # TODO uploadd new file
            data['success'] = True
    else:
        form = RewardAvatarForm();
    
    data['form'] = form
    data['url'] = reverse('reward_avatar', args=[reward_id])
    return render(request, 'manage/avatar_upload.djhtml', data)
    """
    raise  Http404
