from django import forms
from django.utils import timezone
from random import randint
import os, re, datetime

from models import Store, StoreAvatarTmp
from libs.repunch import rputils, rpforms, rpccutils
from libs.repunch.validators import alphanumeric, numeric, required,\
alphanumeric_no_space
from repunch import settings
from parse.apps.accounts.models import Account

class StoreSignUpForm(forms.Form):
    store_name = forms.CharField(max_length=255,
        validators=[required])
    street = forms.CharField(max_length=255,
        validators=[required])
    city = forms.CharField(max_length=255,
        validators=[required])
    state = forms.CharField(max_length=255,
        validators=[required])
    zip = forms.CharField(max_length=255,
        validators=[required, numeric])
    country = forms.CharField(max_length=255,
        validators=[required])
    first_name = forms.CharField(max_length=50,
        validators=[required])
    last_name = forms.CharField(max_length=50,
        validators=[required])
    phone_number = forms.CharField()
    
    recurring = forms.NullBooleanField(widget=forms.CheckboxInput())
    
    def clean_recurring(self):
        data = self.cleaned_data['recurring']
        if not data:
            raise forms.ValidationError("You must accept the Terms"+\
                                    " & Conditions to continue.")
        return data
    
    def get_full_address(self):
        return self.data['street'] + ", " + self.data['city']  + ", " +\
            self.data['state'] + ", " + self.data['zip']  + ", " +\
            self.data['country']
                                    
    def clean_street(self):
        data = self.cleaned_data['street']
        full_address = " ".join(\
            self.get_full_address().split(", "))
        map_data = rputils.get_map_data(full_address)
        # WARNING! get_map_data is unreliable due to google api 
        # query limit!!!!
        if not map_data.get('coordinates'):
            raise forms.ValidationError("Enter a valid adress, city, "+\
                    "state, and/or zip.")
        return data
    
    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        if len(data) < 10:
            raise forms.ValidationError("Enter a valid phone number.")
            
        return data

class StoreForm(forms.Form):
    store_name = forms.CharField(max_length=255,
        validators=[required])
    street = forms.CharField(max_length=255,
        validators=[required])
    city = forms.CharField(max_length=75,
        validators=[required])
    state = forms.CharField(max_length=50,
        validators=[required])
    zip = forms.CharField(max_length=50,
        validators=[required, numeric])
    country = forms.CharField(max_length=50,
        validators=[required])
    phone_number = forms.CharField(max_length=50)
    store_description = forms.CharField(required=False, 
        max_length=500, widget=forms.Textarea(attrs={"maxlength":500}))
             
    def get_full_address(self):
        return self.data['street'] + ", " + self.data['city']  + ", " +\
            self.data['state'] + ", " + self.data['zip']  + ", " +\
            self.data['country']
                                    
    def clean_street(self):
        # WARNING! get_map_data is unreliable due to google api 
        # query limit!!!!
        data = self.cleaned_data['street']
        full_address = " ".join(\
            self.get_full_address().split(", "))
        map_data = rputils.get_map_data(full_address)
        if not map_data.get('coordinates'):
            raise forms.ValidationError("Enter a valid adress, city, "+\
                    "state, and/or zip.")
        return data
                                    
    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        if len(data) < 10:
            raise forms.ValidationError("Enter a valid phone number.")
            
        return data
        
class StoreAvatarForm(forms.Form):
    """
    Returns the ImageFieldFile associated with the StoreAvatar Model
    """
    
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs=\
        {"accept":"image/*"}))
        
   
    def save(self, session_key):    
        def rename():
            #'django.core.files.uploadedfile.InMemoryUploadedFile
            uploaded_img = self.cleaned_data['image']
            # to avoid path conflicts, append a timestamp
            # plus a number from 000 to 999
            uploaded_img._set_name(\
                "".join(uploaded_img.name.split(".")[:-1]) +\
                 timezone.now().strftime("%d%H%M%S") +\
                 str(randint(0, 999)).zfill(3))
            return uploaded_img
        # remove previous session image
        av = StoreAvatarTmp.objects.filter(session_key=session_key)
        if av:
            av = av[0]
            try:
                av.avatar.delete()
            except Exception:
                pass
            finally:
                av.avatar = rename()
                av.save()
        else:
            av = StoreAvatarTmp.objects.create(session_key=\
                session_key, avatar=rename())
        return av.avatar

class SubscriptionSignUpForm(forms.Form):
    """ 
    2s are appended at each attr name because of name conflicts at
    signup with StoreSignUpForm. 
    THIS DOES NOT HAVE THE RECURRING CHECKBOX INPUT!!
    """
    first_name2 = forms.CharField(max_length=100,
                    validators=[alphanumeric, required])
    last_name2 = forms.CharField(max_length=100,
                    validators=[alphanumeric, required])
    cc_number = forms.CharField(max_length=255)
    date_cc_expiration = forms.DateField(widget=rpforms.MonthYearWidget())
    address = forms.CharField(max_length=255,
                    validators=[alphanumeric, required])
    city2 = forms.CharField(max_length=255,
                    validators=[alphanumeric, required])
    state2 = forms.CharField(max_length=255,
                    validators=[alphanumeric, required])
    zip2 = forms.CharField(max_length=255,
        validators=[numeric, required])
    country2 = forms.ChoiceField(choices=[('US', 
                                    'United States of America')])
                                    
    cc_cvv = forms.CharField(validators=[required, numeric])
    
    def clean(self, *args, **kwargs):
        super(SubscriptionSignUpForm, self).clean()
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
    
    def clean_date_cc_expiration(self):
        data = self.cleaned_data['date_cc_expiration']
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
    """
    Use for existing subscriptions. Reason is to not validate credit
    card number but rather just check if it matches the one on record.
    """
    first_name = forms.CharField(max_length=50,
                    validators=[alphanumeric, required])
    last_name = forms.CharField(max_length=50,
                    validators=[alphanumeric, required])
    cc_number = forms.CharField(max_length=255)
    date_cc_expiration = forms.DateField(widget=rpforms.MonthYearWidget())
    address = forms.CharField(max_length=255,
                    validators=[alphanumeric, required])
    city = forms.CharField(max_length=255,
                    validators=[alphanumeric, required])
    state = forms.CharField(max_length=255,
                    validators=[alphanumeric, required])
    zip = forms.CharField(max_length=255,
                    validators=[required, numeric])
    country = forms.ChoiceField(choices=[('US', 
                                    'United States of America')])

    cc_cvv = forms.CharField(validators=[required, numeric])
    recurring = forms.NullBooleanField(widget=forms.CheckboxInput())
    
    
    def clean_cc_number(self):
        """ do not validate_checksum """
        data = str(self.cleaned_data['cc_number'])
        # completely new card number (no asterisks)
        if str(data).isdigit():
            if rpccutils.validate_checksum(data) == False:
                raise forms.ValidationError(\
                    "Enter a valid credit card number.")
            if rpccutils.validate_cc_type(data) == False:
                raise forms.ValidationError(\
                    "Credit card type is not accepted.")
        
        else: # old card number
            data = data[-4:]
            if data != self.subscription.cc_number[-4:]:
                # also check if number changed 
                raise forms.ValidationError(\
                    "Enter a valid credit card number.")
                                            
        return self.cleaned_data['cc_number']
                                        
    def clean(self, *args, **kwargs):
        """ override the clean method. """
        return self.cleaned_data
    
    def clean_recurring(self):
        data = self.cleaned_data['recurring']
        if not data:
            raise forms.ValidationError("You must accept the Terms"+\
                                    " & Conditions to continue.")
        return data
    
    def clean_date_cc_expiration(self):
        data = self.cleaned_data['date_cc_expiration']
        now = datetime.datetime.now()
        if data.year == now.year:
            if data.month < now.month:
                raise forms.ValidationError("Your credit card has"+\
                                            " expired!")
            
        return data
        
               
class SettingsForm(forms.Form):
    punches_employee = forms.IntegerField(label=\
                        'Number of punches allowed by an employee'+\
                        ' at one time', min_value=1, max_value=99)
    punches_facebook = forms.IntegerField(label=\
                        'Free Punch Allowance for Facebook',
                                        min_value=0, max_value=99)
