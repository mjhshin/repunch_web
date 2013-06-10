from django import template
import datetime

from libs.repunch.rphours_util import HoursInterpreter

from parse.apps.messages import UNREAD
from parse.apps.messages.models import Message
from parse.apps.employees import PENDING
from parse.apps.employees.models import Employee

register = template.Library()

@register.assignment_tag
def feedback_unread(store):
    return store.get("receivedMessages", is_read=False, 
                    count=1, limit=0)

@register.assignment_tag
def employees_pending(store):
    return Employee.objects().count(Store=store.objectId, 
                        status=PENDING)

@register.simple_tag
def hours(store):
    #return HoursInterpreter(hours=\
    #    Hours.objects().filter(Store=store.objectId)).readable()   
    return None

@register.simple_tag
def time_selector(fieldid, timestamp):
    
    thour = 10
    tmin = 0
        
    if timestamp != None:
        if isinstance(timestamp, datetime.time):
            thour = timestamp.hour
            tmin = timestamp.minute
        else:
            thour, tmin, _ = timestamp.split(':')
            thour = int(thour)
            tmin = int(tmin)
    
    rv = ['<select id="id_',fieldid,'" name="',fieldid,'">']
    
    # midnight
    if thour == 0:
        rv.extend(('<option ', ('selected' if  tmin == 0 else ''),' value="0:00:00">12:00 AM</option>',
                       '<option ', ('selected' if  tmin == 30 else ''),' value="0:30:00">12:30 AM</option>'))
    else:
        rv.extend(('<option value="0:00:00">12:00 AM</option>',
                   '<option value="0:30:00">12:30 AM</option>'))
    
    # morning
    for hour in range(1, 12):
        if hour == thour:
            rv.extend(('<option ', ('selected' if  tmin == 0  else ''),' value="',str(hour),':00:00">',str(hour),':00 AM</option>',
                       '<option ', ('selected' if  tmin == 30   else ''),' value="',str(hour),':30:00">',str(hour),':30 AM</option>'))
        else:
            rv.extend(('<option value="',str(hour),':00:00">',str(hour),':00 AM</option>',
                       '<option value="',str(hour),':30:00">',str(hour),':30 AM</option>'))
        
    # noon
    if thour == 12:
        rv.extend(('<option ', ('selected' if  tmin == 0  else ''),' value="12:00:00">12:00 PM</option>',
                       '<option ', ('selected' if  tmin == 0  else ''),' value="12:30:00">12:30 PM</option>'))
    else:
        rv.extend(('<option value="12:00:00">12:00 PM</option>',
                   '<option value="12:30:00">12:30 PM</option>'))
        
    for hour in range(1, 12):
        if (hour + 12) == thour:
            rv.extend(('<option ', ('selected' if  tmin == 0 else ''),' value="',str(hour+12),':00:00">',str(hour),':00 PM</option>',
                       '<option ', ('selected' if  tmin == 30 else ''),' value="',str(hour+12),':30:00">',str(hour),':30 PM</option>'))
        else:
            rv.extend(('<option value="',str(hour+12),':00:00">',str(hour),':00 PM</option>',
                       '<option value="',str(hour+12),':30:00">',str(hour),':30 PM</option>'))

    rv.append('</select>')
    return ''.join(rv)
