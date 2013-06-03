from django import forms
import os

from models import Store
from libs.repunch import rputils
from repunch import settings

class StoreSignUpForm(forms.Form):
    store_name = forms.CharField(max_length=255)
    street = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    state = forms.CharField(max_length=255)
    zip = forms.CharField(max_length=255)
    country = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=255)

class StoreForm(StoreSignUpForm):
    phone_number = forms.CharField(max_length=255)
    store_description = forms.CharField(max_length=200, 
                                    widget=forms.Textarea())
        
        
class StoreAvatarForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ('store_avatar',)
        
    def save(self, force_insert=False, force_update=False, commit=True):    
            
        if self.instance != None:
            store = Store.objects.filter().get(id=self.instance.id)
            if store.store_avatar:
                try:                
                    store.store_avatar.delete()
                except Exception:
                    pass # do nothing, 
                
        store = super(StoreAvatarForm, self).save()
        if store != None:
            rputils.rescale(os.path.join(settings.MEDIA_ROOT, store.store_avatar.name))
        
        return store
    
