from django import forms
from django.utils import timezone

from models import Message


class MessageForm(forms.Form):
    subject = forms.CharField(max_length=100)
    body = forms.CharField(max_length=255, 
        widget=forms.Textarea(attrs={"cols":40, "rows":10}))

    attach_offer = forms.BooleanField(required=False)
    offer_title = forms.CharField(max_length=100, required=False)
    date_offer_expiration = forms.DateTimeField(input_formats=['%m/%d/%Y %I:%M %p'], required=False)
    
   
    def __init__(self, *args, **kwargs):   
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['offer_title'].required = False
        self.fields['date_offer_expiration'].required = False
        
    def clean_offer_title(self):
        title = self.cleaned_data['offer_title']
        
        if self.cleaned_data['attach_offer']:
            if title == None or len(title) == 0:
                raise forms.ValidationError('Please enter a title.')
        else:
            title = None
        
        return title
    
    def clean_offer_expiration(self):
        exp = self.cleaned_data['offer_expiration']
        
        if self.cleaned_data['attach_offer']:
            if exp == None:
                raise forms.ValidationError('Please enter an expiration date.')
            else:
                #make sure the expiration is in the future
                now = timezone.now()
                if now >= exp:
                    raise forms.ValidationError('Please enter an expiration date that is later than today.')
        else:
            exp = None
                
        return exp
