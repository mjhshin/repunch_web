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
