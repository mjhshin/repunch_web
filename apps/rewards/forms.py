from django import forms
from models import Reward
import os

from libs.repunch import rputils
from repunch import settings

class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        exclude = ('store', 'reward_avatar', 'redemptions')
        
class RewardAvatarForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ('reward_avatar',)
        
    def save(self, force_insert=False, force_update=False, commit=True):    
            
        if self.instance != None:
            reward = Reward.objects.filter().get(id=self.instance.id)
            if reward.reward_avatar:
                try:                
                    reward.reward_avatar.delete()
                except Exception:
                    pass # do nothing, 
                
        reward = super(RewardAvatarForm, self).save()
        if reward != None:
            rputils.rescale(os.path.join(settings.MEDIA_ROOT, reward.reward_avatar.name))
        
        return reward