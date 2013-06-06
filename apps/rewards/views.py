from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
import urllib

from parse.auth.decorators import login_required
from apps.rewards.forms import RewardForm, RewardAvatarForm

@login_required
def index(request):
    data = {'rewards_nav': True}
    store = request.session['account'].get('store')
    
    print store.get('rewards')
    data['rewards'] = store.get('rewards')
    
    if request.GET.get("success"):
        data['success'] = request.GET.get("success")
    if request.GET.get("error"):
        data['error'] = request.GET.get("error")
    
    return render(request, 'manage/rewards.djhtml', data)


@login_required
def edit(request, reward_id):
    data = {'rewards_nav': True}
    # reward key is now just an array key
    account = request.session['account']
    store = account.get('store')
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
                        "punches":None}
        else: # reward exists
            old_reward = rewards[reward_id]
    else: 
        raise Http404
    
    if request.method == 'POST': 
        form = RewardForm(request.POST) 
        if form.is_valid():
            reward = {'reward_name':form.data['reward_name'], 
                "description":form.data['description'], 
                "punches":form.data['punches']}
  
            if not is_new:
                store.array_remove('rewards', [old_reward])

            store.array_add_unique('rewards', [reward])

            
            now_count = len(store.get('rewards'))
            if now_count > init_count:
                reward_id = now_count - 1
            
            #reload the store and put it in the session
            account.store = store
            request.session['account'] = account
            data['reward_id'] = len(store.get('rewards'))
            if not is_new:
                data['success'] = "Reward has been updated."
            else:
            # Since this is new we need to redirect the page
                return HttpResponseRedirect(\
                    reverse('reward_edit', args=[reward_id])+ "?%s" %\
                     urllib.urlencode({'success':\
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

    data['is_new'] = is_new;
    data['reward'] = reward
    data['reward_id'] = reward_id
    data['form'] = form
    return render(request, 'manage/reward_edit.djhtml', data)

@login_required
def delete(request, reward_id):
    account = request.session['account']
    store = account.get('store')
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
    account.store = store
    request.session['account'] = account
    return redirect(reverse('rewards_index')+\
                "?%s" % urllib.urlencode({'success':\
                'Reward has been removed.'}))


@login_required
def avatar(request, reward_id):
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
