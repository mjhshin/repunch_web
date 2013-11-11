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
    count = 0
    for fb in SESSION.get_messages_received_list(session):
        if not fb.get("is_read"):
            count += 1
    return count

@register.assignment_tag
def employees_pending(session):
    return len(SESSION.get_employees_pending_list(session))
    
@register.assignment_tag
def redemptions_pending(session):
    return len(SESSION.get_redemptions_pending(session))

@register.simple_tag
def hours(session):
    """ 
    build the list of hours in proper format to render in template
    """
    # TODO
    return HoursInterpreter(hours=hours).readable()  

@register.simple_tag
def time_selector(name, timestamp):
    """
    Returns a select block with options from 6am to 5.30 am in 30 min
    increments. 
    
    Time is represented as XXyy where XX is the hours from 00 to 23
    and yy is the minutes, which is either 00 or 30.
    
    The generated select has the following format:
    
    <select name=name>
        <option value="0600">6:00 AM</option>
        <option value="0630">6:30 AM</option>
        ...
        <option value="1200">12 PM (Noon)</option>
        ...
        <option value="0000">12 AM (Midnight)</option>
        ...
        <option value="0530">5:30 AM</option>
    </select>
    
    The optional parameter timestamp determines which option is selected.
    """
    def option_text(value):
        """
        Returns the text of the option given the value.
        e.g. option_text("0630") returns 6:30 AM.
        """
        if value == "0000":
            return "12 AM (Midnight)"
        elif value == "1200":
            return "12 PM (Noon)"
        else:
            hour = int(value[0:2])
            if hour >= 12:
                if hour > 12:
                    hour -= 12
                ampm = "PM"
            else:
                if hour == 0:
                    hour = 12
                ampm = "AM"
                
            return "%s:%s %s" % (str(hour), value[2:], ampm)
                
    
    select = "<select name='%s'>%s</select>"
    options = []
    
    option = "<option value='%s'>%s</option>"
    option_selected = "<option value='%s' selected>%s</option>"
    
    # generate the options
    start_hour = 6
    for i in range(24): # 24 hours
        # TODO determine if selected
        opt = option
        hour = str((i+start_hour)%24).zfill(2)
        
        options.append(opt % (hour+"00", option_text(hour+"00")))
        options.append(opt % (hour+"30", option_text(hour+"30")))
    
    return select % (name, "".join(options))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
