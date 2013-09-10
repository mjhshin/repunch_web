from django import forms
from django.core.mail import send_mail

from libs.repunch.validators import required
from repunch.settings import EMAIL_FROM, ORDER_PLACED_EMAILS, DEBUG

SUBJECT_PREFIX = "Contact Form - "
    
class ContactForm(forms.Form):
    full_name = forms.CharField(max_length=100,required=True,
        validators=[required])
    email = forms.EmailField(required=True, validators=[required])
    message = forms.CharField(widget=forms.Textarea, required=True,
        validators=[required])
    
    # send email to administrator
    def send(self):
        full_message = "Someone has filled out the contact form on"+\
           " repunch\r\nName: %s\r\nEmail: %s\r\nMessage:\r\n %s" %\
                (self.cleaned_data['full_name'], 
                self.cleaned_data['email'], 
                self.cleaned_data['message'])

        send_mail(SUBJECT_PREFIX + self.cleaned_data['full_name'], 
                full_message, EMAIL_FROM, 
                ORDER_PLACED_EMAILS, fail_silently=not DEBUG)
