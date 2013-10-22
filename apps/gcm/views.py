"""
Processes POST requests from Cloud Code and sends corresponding 
GCM HTTP Server.
""" 

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from libs.gcm import gcm_send

from django.core.mail import send_mail
from repunch.settings import EMAIL_FROM, ORDER_PLACED_EMAILS, DEBUG

@csrf_exempt
def receive(request):
    if request.method == "POST":
        try:
            postDict = json.loads(unicode(request.body, "ISO-8859-1"))
        except Exception:
            return HttpResponse("error")
            
            
        send_mail("ASFASFF", str(postDict), EMAIL_FROM, 
            ["vandolf@repunch.com"], fail_silently=not DEBUG)
        
        if gcm_send(postDict):
            return HttpResponse("success")
            
    return HttpResponse("error")
