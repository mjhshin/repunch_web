"""
Processes POST requests from Cloud Code and sends corresponding 
GCM HTTP Server.
""" 

from libs.gcm import gcm_send

def receive(request):
    if request.method == "POST":
        try:
            postDict = json.loads(unicode(request.body, "ISO-8859-1"))
        except Exception:
            return HttpResponse("error")
        
        if gcm_send(postDict):
            return HttpResponse("success")
            
    return HttpResponse("error")
