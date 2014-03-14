"""
Views for the Rewards tab in the dashboard.
"""

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
import urllib, json

from repunch.settings import COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY
from parse import session as SESSION
from parse.comet import comet_receive
from parse.decorators import admin_only, access_required
from parse.auth.decorators import login_required, dev_login_required
from apps.rewards.forms import RewardForm

@dev_login_required
@login_required
@access_required
def index(request):
    """
    Render the rewards template with the store's rewards.
    """
    data = {'rewards_nav': True}
    store = SESSION.get_store(request.session)
    lst, rewards = [], store.get('rewards')
    
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
        
    # store has no rewards =(
    else:
        data['rewards'] = []
    
    # inserting this success and error message into the template
    # should be done in a cleaner way - this was done by the first guy
    # I just didn't bother changing it.
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
        
    # update session cache
    request.session['store'] = store
    
    return render(request, 'manage/rewards.djhtml', data)


@dev_login_required
@login_required
@admin_only(reverse_url="rewards_index")
def edit(request, reward_id):
    """
    Render the reward edit template for a new or existing reward or
    handle forms for new or existing rewards.
    """

    # check if the reward_id passed in is invalid and raise a 404 if so.
    # reward ids are integers
    try:
        reward_id = int(str(reward_id))
    except ValueError:
        raise Http404
        
    data = {'rewards_nav': True}
    store = SESSION.get_store(request.session)
    rewards = store.get('rewards')
    rewards_map = { reward['reward_id']:reward for reward in rewards }
 
    # reward id being -1 is a flag for new reward which don't exist
    is_new, reward = reward_id == -1, None
    
    if reward_id in rewards_map:
        reward = rewards_map[reward_id]
    
    elif reward_id not in rewards_map and not is_new: 
        # the reward with the given reward id does not exist nor
        return redirect(reverse('rewards_index'))
    
    # user submits form
    if request.method == 'POST': 
        form = RewardForm(request.POST) 
        if form.is_valid():
            # construct a reward dict from the form
            reward = {'reward_name':form.data['reward_name'], 
                "description":" ".join(form.data['description'].split()), 
                "punches":int(form.data['punches']),
                "redemption_count":0}
                
            # create a list of sorted ids from the rewards
            ids, msg = [ r['reward_id'] for r in rewards], ""
            ids.sort()           
  
            if not is_new:
                msg = 'Reward has been updated.'
                
                # we have an existing reward - we need to carry over
                # the previous redemption_count if user did not
                # specify to reset it
                old_reward = rewards_map[reward_id]
                if not request.POST.get('reset_red_count'):
                    reward["redemption_count"] =\
                        old_reward["redemption_count"]
                        
                # the reward_id will not change
                reward['reward_id'] = old_reward['reward_id']
                # remove the old_reward from Parse since we will
                # add our created reward instance later
                store.array_remove('rewards', [old_reward])
                
            elif len(ids) == 0: 
                # store's very first reward
                msg = 'Reward has been added.'
                reward['reward_id'] = 0
                
            else:
                # reward is new so assign the highest id + 1
                msg = 'Reward has been added.'
                reward['reward_id'] = ids[-1] + 1
                
            # notify other dashboards of this change
            if is_new:
                comet_attr = 'newReward'
            else:
                comet_attr = 'updatedReward'
                
            comet_receive(store.objectId, {
                COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
                comet_attr: reward
            })
            
            # add our reward to Parse
            store.array_add_unique('rewards', [reward])
            
            # update session cache
            store.rewards = None
            store.get('rewards')
            request.session['store'] = store
            
            return redirect(reverse('rewards_index')+\
                "?%s" % urllib.urlencode({'success':msg}))
    else:
        form = RewardForm(reward)
            
    data.update({
        'reward': reward,
        'is_new': is_new,
        'reward_id': reward_id,
        'form': form,
    
    })
    return render(request, 'manage/reward_edit.djhtml', data)

@dev_login_required
@login_required
@admin_only(reverse_url="rewards_index")
def delete(request, reward_id):
    """
    Deletes a reward with the given reward_id.
    """
    
    # check if the reward_id passed in is invalid and raise a 404 if so.
    # reward ids are integers
    try:
        reward_id = int(str(reward_id))
    except ValueError:
        raise Http404
        
    account = request.session['account']
    store = SESSION.get_store(request.session)
    rewards = store.get('rewards')
    rewards_map = { reward['reward_id']:reward for reward in rewards }

    # reward cannot be found for deletion. Redirect user to the rewards
    # page with a success message (maybe this should be an error message instead?).
    try: 
        reward = rewards_map[reward_id]
    except KeyError:
        return redirect(reverse('rewards_index')+\
                "?%s" % urllib.urlencode({'success':\
                'Reward has been removed.'}))
    
    # notify other dashboards of this change
    payload = {
        COMET_RECEIVE_KEY_NAME: COMET_RECEIVE_KEY,
        "deletedReward": {"reward_id":reward["reward_id"]}
    }
    comet_receive(store.objectId, payload)
    
    # update session cache
    store.array_remove('rewards', [reward])
    store.rewards = None
    store.get('rewards')
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
