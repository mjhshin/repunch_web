from django import forms
from models import Reward
import os

from libs.repunch import rputils
from repunch import settings
from libs.repunch.validators import required

class RewardForm(forms.Form):
    reward_name = forms.CharField(max_length=40,
        validators=[required])
    description = forms.CharField(max_length=125, 
        widget=forms.Textarea(\
        attrs={"maxlength":125}), required=False)
    punches = forms.IntegerField(min_value=1, max_value=999)
        
class RewardAvatarForm(forms.Form):
    employee_avatar = forms.FileField()
    """
    class Meta:
        model = Reward
        fields = ('reward_avatar',)
        
    def save(self, force_insert=False, force_update=False,
                commit=True):    
            
        if self.instance != None:
            reward = Reward.objects.filter().get(id=self.instance.id)
            if reward.reward_avatar:
                try:                
                    reward.reward_avatar.delete()
                except Exception:
                    pass # do nothing, 
                
        reward = super(RewardAvatarForm, self).save()
        if reward != None:
            rputils.rescale(os.path.join(settings.MEDIA_ROOT,
                reward.reward_avatar.name))
        
        return reward
    """
