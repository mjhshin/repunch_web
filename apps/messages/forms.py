from django import forms
from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from models import Message


class MessageForm(forms.Form):
    subject = forms.CharField(max_length=50)
    body = forms.CharField(max_length=750, 
        widget=forms.Textarea(attrs={"cols":40, "rows":10, "maxlength":750}))

    attach_offer = forms.BooleanField(required=False)
    offer_title = forms.CharField(max_length=30, required=False)
    date_offer_expiration = forms.DateTimeField(input_formats=['%m/%d/%Y %I:%M %p'], required=False)
    num_patrons = forms.CharField(max_length=7, required=False)
    
   
    def __init__(self, *args, **kwargs):   
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['offer_title'].required = False
        self.fields['date_offer_expiration'].required = False
        
    def clean_num_patrons(self):
        try:
            num = int(self.cleaned_data['num_patrons'])
            if num < 1:
                raise forms.ValidationError(\
                    'Number of customers must at least 1.')
        except ValueError:
            raise forms.ValidationError('Number of customers must '+\
                'be a whole number.')
        
    def clean_offer_title(self):
        title = self.cleaned_data['offer_title']
        
        if self.cleaned_data['attach_offer']:
            if title == None or len(title) == 0:
                raise forms.ValidationError('Please enter a title.')
        else:
            title = None
        
        return title
    
    def clean_date_offer_expiration(self):
        exp = self.cleaned_data['date_offer_expiration']
        
        if self.cleaned_data['attach_offer']:
            if exp == None:
                raise forms.ValidationError('Please enter an expiration date.')
            else:
                # make sure the expiration is in the future
                now = timezone.now()
                if now >= exp:
                    raise forms.ValidationError('Please enter an'+\
                        ' expiration date that is later than today.')
                # max is 1 year
                year_later = now + relativedelta(years=1)
                if exp >= year_later:
                    raise forms.ValidationError('Please enter an'+\
                        ' expiration date that is less than a year.')
                    
        else:
            exp = None
                
        return exp
