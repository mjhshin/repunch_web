from django import template
import datetime

from libs.repunch.rphours_util import HoursInterpreter

from apps.stores.models import Hours
from parse.apps.messages import FEEDBACK
from parse.apps.messages.models import Message
from parse.apps.employees import PENDING
from parse.apps.employees.models import Employee
from parse import session as SESSION

register = template.Library()

@register.assignment_tag
def feedback_unread(session):
    """ this is just a count of # of unread feedbacks """
    return SESSION.get_feedback_unread(session)


@register.assignment_tag
def employees_pending(session):
    return SESSION.get_employees_pending(session)

@register.simple_tag
def hours(session):
    """ 
    build the list of hours in proper format to render in template
    """
    hours_map, hours = {}, []
    store = SESSION.get_store(session)
    hrs = store.get("hours")
    if hrs:
        for hour in hrs:
            key = (hour['close_time'], hour['open_time'])
            if key in hours_map:
                hours_map[key].append(hour['day'])
            else:
                hours_map[key] = [hour['day']]
        for i, key in enumerate(hours_map.iterkeys()):
            hours.append(Hours(days=\
                    [str(d) for d in hours_map[key]],
                    open=datetime.datetime.strptime(key[1], "%H%M"),
                    close=datetime.datetime.strptime(key[0], "%H%M"),
                    list_order=i+1))
                    
    # update the session cache
    session['store'] = store
            
    return HoursInterpreter(hours=hours).readable()  

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
