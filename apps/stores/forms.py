from django import forms
from django.utils import timezone
from django.core.files.images import get_image_dimensions
from random import randint
import os, re, datetime

from models import Store, UploadedImageFile
from libs.repunch import rputils, rpforms, rpccutils
from libs.repunch.validators import alphanumeric, numeric, required,\
alphanumeric_no_space
from parse.apps.accounts.models import Account
from repunch.settings import IMAGE_COVER_MIN_EDGE,\
IMAGE_COVER_ASPECT_RATIO_RANGE

class StoreLocationForm(forms.Form):
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
    phone_number = forms.CharField()
    
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

class StoreSignUpForm(forms.Form):
    store_name = forms.CharField(max_length=255,
        validators=[required])
    first_name = forms.CharField(max_length=50,
        validators=[required])
    last_name = forms.CharField(max_length=50,
        validators=[required])
    
    recurring = forms.NullBooleanField(widget=forms.CheckboxInput())
    
    def clean_recurring(self):
        data = self.cleaned_data['recurring']
        if not data:
            raise forms.ValidationError("You must accept the Terms"+\
                                    " & Conditions to continue.")
        return data

class StoreForm(forms.Form):
    store_name = forms.CharField(max_length=255,
        validators=[required])
    store_description = forms.CharField(required=False, 
        max_length=500, widget=forms.Textarea(attrs={"maxlength":500}))
        
class UploadImageForm(forms.Form):
    """
    Returns the ImageFieldFile associated with the session 
    """
    
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs=\
        {"accept":"image/*"}))
        
    def clean_image(self):
        """
        The aspect ratio must be from 16:9 to 9:16.
        The shortest edge must be at least IMAGE_COVER_MIN_EDGE.
        
        We do not check for the longest edge. If we happen to exceed
        it, we will simply scale to down to IMAGE_COVER_MAX_EDGE and
        maintain the aspect ratio.
        """
        image = self.cleaned_data.get("image")
        
        if not image:
            raise forms.ValidationError(\
                "Image is corrupted or not supported.")
                
        width, height = get_image_dimensions(image)
        width, height = float(width), float(height)

        # first check for aspect ratio
        min_aspect, max_aspect = IMAGE_COVER_ASPECT_RATIO_RANGE
        min_aspect = min_aspect[0] / min_aspect[1]
        max_aspect = max_aspect[0] / max_aspect[1]
        
        if height <= 0.0: # prevent division by 0
            img_aspect = 0.0
        else:
            img_aspect = width/height
            
        if img_aspect < min_aspect or img_aspect > max_aspect:
            raise forms.ValidationError(\
                "Image aspect ratio must be between 16:9 and 9:16")
                
        # now check for min and max edges
        if width < height and width < IMAGE_COVER_MIN_EDGE:
            raise forms.ValidationError(\
                "Image width must be at least " + str(IMAGE_COVER_MIN_EDGE))
        
        elif width > height and height < IMAGE_COVER_MIN_EDGE:
            raise forms.ValidationError(\
                "Image height must be at least " + str(IMAGE_COVER_MIN_EDGE))
            
        elif width == height and width < IMAGE_COVER_MIN_EDGE:
            raise forms.ValidationError(\
                "Image width must be at least " + str(IMAGE_COVER_MIN_EDGE))
            
        return image
   
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
        img = UploadedImageFile.objects.filter(session_key=session_key)
        if img:
            img = img[0]
            try:
                img.image.delete()
            except Exception:
                pass
            finally:
                img.image = rename()
                img.save()
        else:
            img = UploadedImageFile.objects.create(session_key=\
                session_key, image=rename())
                
        return img.image
        
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
