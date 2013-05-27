from django import forms
import os

from models import Store
from libs.repunch import rputils
from repunch import settings

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        exclude = ('store_avatar', 'active_users', 'store_timezone')
        
class StoreSignUpForm(forms.ModelForm):
    """ PARSE SAFE """
    class Meta:
        model = Store
        exclude = ('phone_number', 'store_description',
                 'store_avatar', 'active_users', 'store_timezone')
        
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
    
