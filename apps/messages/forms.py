from django import forms
from django.utils import timezone

from models import Message


class MessageForm(forms.ModelForm):
    offer_expiration = forms.DateTimeField(input_formats=['%m/%d/%Y %I:%M %p'])
    class Meta:
        model = Message
        exclude = ('store', 'sent_to_recipients_count')
        
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)        
        super(MessageForm, self).__init__(*args, **kwargs)
        
        self.fields['offer_expiration'].required = False
        
    def clean_status(self):
        if self.data['action'] == 'send' and self.account.get_sents_available() <= 0:
            raise forms.ValidationError('MaxReached')
        else:
            if self.data['action'] == 'send':
                self.cleaned_data['status'] = 'Sent'
            else:
                self.cleaned_data['status'] = 'Draft'
            
        return self.cleaned_data['status']
    
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
