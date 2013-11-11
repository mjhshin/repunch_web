"""
Hours interpreter re-written.
"""

from parse.apps.stores import models

# no ambiguity here lol
WEEKDAYS = {
    1: 'Sunday',
    2: 'Monday',
    3: 'Tuesday',
    4: 'Wednesday',
    5: 'Thursday',
    6: 'Friday',
    7: 'Saturday',
}

def readable_hours(value):
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
        
def readable_hours_range(open_time, close_time):
    return readable_hours(open_time)+"  -  "+readable_hours(close_time)
    
def readable_days_list(days):
    days.sort()
    return " and ".join([ WEEKDAYS[i] for i in days ])   
    
def get_adj_days(day, days, group=[]):
    """
    Returns the adjacent days relative to day and groups them up in a
    list. The adjacent days are popped from days.
    
    The day is popped from the days immediately even if it does not
    have any adjacent days.
    
    Slick recurseion is used here. =)
    """
    group.append(days.pop(days.index(day)))
            
    def left_adj(d):
        left = d-1
        if left == 0:
            left = 7
        if left in days:
            group.append(days.pop(days.index(left)))
            left_adj(left)
            
        
    def right_adj(d):
        right = d+1
        if right == 8:
            right = 1
        if right in days:
            group.append(days.pop(days.index(right)))
            right_adj(right)

    # time to recursively collect the adjacent days
    left_adj(day)
    right_adj(day) 
        
    # sort before returning
    group.sort()
    return group
            
class HoursInterpreter:
    def __init__(self, hours):
        self.hours = hours
        
    def readable(self):        
        """
        Example return value:
        Sundays and Monday - Friday  6:00 AM - 1:30 PM<br/>
        Wednesdays and Fridays  3:30 PM  - 11:30 PM<br/>
        Closed Sundays and Saturdays
        """
        readable, hours_map = [], {}
        # first create a map with the open and close time as the keys
        for k, v in self.hours.iteritems():
            # v is hours-x-day_y
            if v not in hours_map:
                hours_map[v] = []
            hours_map[v].append(int(k.split("_")[-1]))
        
        # TODO FIX BUGS
        
        # now process each set of open and close time
        for k, v in hours_map.iteritems():
            open_time, close_time = k.split(",")
            # days start from 1 to 7 and is circular so we must group
            # adjacent elements together first
            groups, solos = [], []
            while len(v) > 0:
                group = get_adj_days(v[0], v)
                if len(group) == 1: # no adjacent
                    solos.extend(group)
                else:
                    groups.append(group)
              
            line = ""
            # make readable process solo days
            line += readable_days_list(solos)
            # make readable grouped days
            while len(groups) > 0:
                group = groups.pop(0)
                start, end = min(group), max(group)
                line += " and "
                
                # case that there is a gap in b/w the min and max
                if set(group) != set(range(start, end+1)): # e.g 1,2,5,6,7
                    # find the left most day from the max before the gap
                    while True:
                        if end - 1 not in group:
                            break;
                        end-=1
                    # find the right most day from the min before the gap
                    while True:
                        if start + 1 not in group:
                            break;
                        start+=1
                        
                    # swap 
                    tmp = start
                    start = end
                    end = tmp
                        
                line += WEEKDAYS[start]+"  -  "+WEEKDAYS[end]
                
            line += "  "+readable_hours_range(open_time, close_time)
                
            readable.append(line) 
            
            # make the closed days (if any) readable
            
        
        return "".join(readable)
    
