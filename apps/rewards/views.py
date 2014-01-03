from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
import urllib, json

from repunch.settings import COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY
from parse import session as SESSION
from parse.comet import comet_receive
from parse.decorators import admin_only, access_required
from parse.auth.decorators import login_required, dev_login_required
from apps.rewards.forms import RewardForm, RewardAvatarForm

@dev_login_required
@login_required
@access_required
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
    
    
    for v in SESSION.get_store(request.session).store_locations:
        print "##############"
        print v.__dict__
    
    return render(request, 'manage/rewards.djhtml', data)


@dev_login_required
@login_required
@admin_only(reverse_url="rewards_index")
def edit(request, reward_id):
    data = {'rewards_nav': True}
    store = SESSION.get_store(request.session)
    rewards = store.get('rewards')
    rewards_map = { reward['reward_id']:reward for reward in rewards }

    try:
        reward_id = int(str(reward_id))
    except ValueError:
        raise Http404
 
    # reward id being -1 is a flag for new reward which don't exist
    is_new, reward = False, None
    if reward_id in rewards_map: # reward exists
        old_reward = rewards_map[reward_id]
        
    elif reward_id == -1:
        is_new = True
        # a reward is now just a dictionary to be added to 
        # the rewards array
        reward = {'reward_name':None, "description":None, 
                    "punches":None, 'redemption_count':0}
                    
    else: 
        return redirect(reverse('rewards_index'))
    
    if request.method == 'POST': 
        form = RewardForm(request.POST) 
        if form.is_valid():
            # the description is stripped of newlines and tabs.
            reward = {'reward_name':form.data['reward_name'], 
                "description":" ".join(form.data['description'].split()), 
                "punches":int(form.data['punches']),
                "redemption_count":0}
                
            # assign a new reward_id
            ids, msg = [], ""
            for r in rewards:
                ids.append(r.get("reward_id"))
            ids.sort()           
  
            if not is_new:
                msg = 'Reward has been updated.'
                # reset the redemtion count?
                if request.POST.get('reset_red_count'):
                    reward["redemption_count"] = 0
                else:
                    reward["redemption_count"] =\
                        old_reward["redemption_count"]
                reward['reward_id'] = old_reward['reward_id']
                store.array_remove('rewards', [old_reward])
            elif len(ids) == 0: # first reward
                msg = 'Reward has been added.'
                reward['reward_id'] = 0
            else:
                msg = 'Reward has been added.'
                reward['reward_id'] = ids[-1] + 1
                
            # notify other dashboards of this change
            if is_new:
                payload = {
                    COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                    "newReward":reward
                }
            else:
                payload = {
                    COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                    "updatedReward":reward
                }
                
            comet_receive(store.objectId, payload)
            
            store.array_add_unique('rewards', [reward])
            store.rewards = None
            store.get('rewards')
            
            # update session cache
            request.session['store'] = store
            
            return redirect(reverse('rewards_index')+\
                "?%s" % urllib.urlencode({'success':msg}))
    else:
        if reward_id >= 0 and reward_id in rewards_map:
            reward = rewards_map[reward_id]
            form = RewardForm(reward)
            data['reward'] = reward
        else:
            form = RewardForm()
        if not is_new:
            if request.GET.get("success"):
                data['success'] = request.GET.get("success")
            if request.GET.get("error"):
                data['error'] = request.GET.get("error")
                
    # update session cache
    request.session['store'] = store

    data['is_new'] = is_new
    data['reward_id'] = reward_id
    data['form'] = form
    return render(request, 'manage/reward_edit.djhtml', data)

@dev_login_required
@login_required
@admin_only(reverse_url="rewards_index")
def delete(request, reward_id):
    account = request.session['account']
    store = SESSION.get_store(request.session)
    rewards = store.get('rewards')
    rewards_map = { reward['reward_id']:reward for reward in rewards }

    try:
        reward_id = int(str(reward_id))
    except ValueError:
        raise Http404
    
    try: 
        reward = rewards_map[reward_id]
    except KeyError:
        return redirect(reverse('rewards_index')+\
                "?%s" % urllib.urlencode({'success':\
                'Reward has been removed.'}))
    
    store.array_remove('rewards', [reward])
    store.rewards = None
    store.get('rewards')
    
    # notify other dashboards of this change
    payload = {
        COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
        "deletedReward": {"reward_id":reward["reward_id"]}
    }
    comet_receive(store.objectId, payload)
    
    # update session cache
    request.session['store'] = store
    
    return redirect(reverse('rewards_index')+\
                "?%s" % urllib.urlencode({'success':\
                'Reward has been removed.'}))


@dev_login_required
@login_required
def avatar(request, reward_id):
    """
    Unused at the moment
    """
    raise  Http404
