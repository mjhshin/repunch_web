from django import forms
from django.core.mail import send_mail

from repunch.settings import ORDER_PLACED_EMAILS

class ContactForm(forms.Form):
    full_name = forms.CharField(max_length=100,required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    
    # send email to administrator
    def send(self):
        full_message = "Someon has filled out the contact form on"+\
           " repunch\r\nName: %s\r\nEmail: %s\r\nMessage:\r\n %s" %\
                (self.cleaned_data['full_name'], 
                self.cleaned_data['email'], 
                self.cleaned_data['message'])

        send_mail("Contact Form", full_message, 
                self.cleaned_data['email'], ORDER_PLACED_EMAILS,
                fail_silently=True)
