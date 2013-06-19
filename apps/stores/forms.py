from django import forms
import os, re, datetime

from models import Store
from libs.repunch import rputils, rpforms, rpccutils
from libs.repunch.validators import alphanumeric
from repunch import settings

class StoreSignUpForm(forms.Form):
    store_name = forms.CharField(max_length=255)
    street = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    state = forms.CharField(max_length=255)
    zip = forms.CharField(max_length=255)
    country = forms.CharField(max_length=255)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    phone_number = forms.CharField()
    
    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        if len(data) < 10:
            raise forms.ValidationError("Enter a valid phone number.")
            
        return data

class StoreForm(forms.Form):
    store_name = forms.CharField(max_length=255)
    street = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    state = forms.CharField(max_length=255)
    zip = forms.CharField(max_length=255)
    country = forms.CharField(max_length=255)
    phone_number = forms.CharField(max_length=255)
    store_description = forms.CharField(max_length=200, 
                                    widget=forms.Textarea())
                                    
    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        if len(data) < 10:
            raise forms.ValidationError("Enter a valid phone number.")
            
        return data
        
class StoreAvatarForm(forms.Form):
    store_avatar = forms.FileField()
        
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
    

class SubscriptionForm2(forms.Form):
    """ 
    2s are appended at each attr name because of name confllicts at
    signup with StoreSignUpForm. """
    first_name2 = forms.CharField(max_length=30,
                    validators=[alphanumeric])
    last_name2 = forms.CharField(max_length=100,
                    validators=[alphanumeric])
    cc_number = forms.CharField(max_length=255)
    cc_expiration = forms.DateField(widget=rpforms.MonthYearWidget())
    address = forms.CharField(max_length=255,
                    validators=[alphanumeric])
    city2 = forms.CharField(max_length=255,
                    validators=[alphanumeric])
    state2 = forms.CharField(max_length=255,
                    validators=[alphanumeric])
    zip2 = forms.CharField(max_length=255,
                    validators=[alphanumeric])
    country2 = forms.ChoiceField(choices=[('US', 
                                    'United States of America')])
                                    
    cc_cvv = forms.CharField()
    recurring = forms.NullBooleanField(widget=forms.CheckboxInput())
    
    def clean(self, *args, **kwargs):
        super(SubscriptionForm2, self).clean()
        cleaned_data = self.cleaned_data
        
        # if cc_number doesn't exists, it is because we already 
        # have an error
        if 'cc_number' in cleaned_data:
            cc = cleaned_data['cc_number']
            mask = (len(cc)-4)*'*'
            mask += cc[-4:]
            cleaned_data['cc_number'] = mask
        
            # credit card processing will go here
            # raise forms.ValidationError("Error processing credit"+\
            #                            " card!")
        
        return cleaned_data
    
    def clean_recurring(self):
        data = self.cleaned_data['recurring']
        if not data:
            raise forms.ValidationError("You must accept the Terms"+\
                                    " & Conditions to continue.")
        return data
    
    def clean_cc_expiration(self):
        data = self.cleaned_data['cc_expiration']
        now = datetime.datetime.now()
        if data.year == now.year:
            if data.month < now.month:
                raise forms.ValidationError("Your credit card has"+\
                                            " expired!")
            
        return data
    
    def clean_cc_number(self):
        data = self.cleaned_data['cc_number']
        data = re.sub("[^0-9]", "", data) 

        if rpccutils.validate_checksum(data) == False:
            raise forms.ValidationError("Enter a valid credit card"+\
                                        " number.")
        if rpccutils.validate_cc_type(data) == False:
            raise forms.ValidationError("Credit card type is not"+\
                                        " accepted.")
        
        return data
        
class SubscriptionForm(forms.Form):
    first_name = forms.CharField(max_length=30,
                    validators=[alphanumeric])
    last_name = forms.CharField(max_length=100,
                    validators=[alphanumeric])
    cc_number = forms.CharField(max_length=255)
    cc_expiration = forms.DateField(widget=rpforms.MonthYearWidget())
    address = forms.CharField(max_length=255,
                    validators=[alphanumeric])
    city = forms.CharField(max_length=255,
                    validators=[alphanumeric])
    state = forms.CharField(max_length=255,
                    validators=[alphanumeric])
    zip = forms.CharField(max_length=255,
                    validators=[alphanumeric])
    country = forms.ChoiceField(choices=[('US', 
                                    'United States of America')])

    cc_cvv = forms.CharField()
    recurring = forms.NullBooleanField(widget=forms.CheckboxInput())
    
    def clean(self, *args, **kwargs):
        super(SubscriptionForm, self).clean()
        cleaned_data = self.cleaned_data
        
        # if cc_number doesn't exists, it is because we already 
        # have an error
        if 'cc_number' in cleaned_data:
            cc = cleaned_data['cc_number']
            mask = (len(cc)-4)*'*'
            mask += cc[-4:]
            cleaned_data['cc_number'] = mask
        
            # credit card processing will go here
            # raise forms.ValidationError("Error processing credit"+\
            #                            " card!")
        
        return cleaned_data
    
    def clean_recurring(self):
        data = self.cleaned_data['recurring']
        if not data:
            raise forms.ValidationError("You must accept the Terms"+\
                                    " & Conditions to continue.")
        return data
    
    def clean_cc_expiration(self):
        data = self.cleaned_data['cc_expiration']
        now = datetime.datetime.now()
        if data.year == now.year:
            if data.month < now.month:
                raise forms.ValidationError("Your credit card has"+\
                                            " expired!")
            
        return data
    
    def clean_cc_number(self):
        data = self.cleaned_data['cc_number']
        data = re.sub("[^0-9]", "", data) 

        if rpccutils.validate_checksum(data) == False:
            raise forms.ValidationError("Enter a valid credit card"+\
                                        " number.")
        if rpccutils.validate_cc_type(data) == False:
            raise forms.ValidationError("Credit card type is not"+\
                                        " accepted.")
        
        return data
               
class SettingsForm(forms.Form):
    punches_customer = forms.IntegerField(label=\
                        'Number of separate times a customer can'+\
                        ' receive punches per day', min_value=0)
    punches_employee = forms.IntegerField(label=\
                        'Number of punches allowed by an employee'+\
                        ' at one time', min_value=0)
    punches_facebook = forms.IntegerField(label=\
                        'Free Punch Allowance for Facebook',
                                        min_value=0)
