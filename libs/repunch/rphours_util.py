"""
Hours interpreter re-written.
"""

from apps.stores.models import DAYS, SHORT_DAYS
from parse.apps.stores import models

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
    
def readable_days_list(days, return_type=str, names=DAYS, postfix=""):
    days.sort()
    d = [ names[i-1][1]+postfix for i in days ]
    
    if return_type is str:
        return " and ".join(d)
    elif return_type is list:
        return d
    
def get_adj_days(day, days):
    """
    Returns the adjacent days relative to day and groups them up in a
    list. The adjacent days are popped from days.
    
    The day is popped from the days immediately even if it does not
    have any adjacent days.
    
    Slick recursion is used here. =)
    """
    group = [days.pop(days.index(day))]
            
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
        
    def _to_readable(self, order, hours_map, open=True):
        readable = []
        
        # keep the order of the hours and
        # process each set of open and close time
        for k in order:
            v = hours_map[k]
            # days start from 1 to 7 and is circular so we must group
            # adjacent elements together first
            groups, solos = [], []
            while len(v) > 0:
                group = get_adj_days(v[0], v)
                if len(group) == 1: # no adjacent
                    solos.extend(group)
                else:
                    groups.append(group)
                    
            # use short days if there is more than 1 group or 2 solos
            # pluralize the Days for solos if full day name
            names, postfix, line = DAYS, "s", []
            if len(solos) > 2 or len(groups) > 1 or len(solos) +\
                len(groups) > 2:
                names = SHORT_DAYS
                postfix = ""
            
            # make readable grouped days
            while len(groups) > 0:
                group = groups.pop(0)
                start, end = min(group), max(group)
                
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
                
                # add the groups to the line if any     
                line.append(names[start-1][1]+"  -  "+names[end-1][1])
                
            # add the solo days to the line if any
            line.extend(readable_days_list(solos, list, names, postfix))
                
            # time to add separators
            total, processed_line = len(line), []
            if total > 2: # commas + and
                for l in line:
                    if line.index(l) == total - 1: # last element
                        processed_line.append(" and ")
                        processed_line.append(l)
                    else:
                        processed_line.append(l)
                        processed_line.append(", ")
                     
            elif total == 2: # and
                processed_line.append(line[0])
                processed_line.append(" and ")
                processed_line.append(line[1])
            else: # just 1 element
                processed_line = line
            
            # add the close and open time to the line if these days are open
            if open:
                open_time, close_time = k.split(",")
                processed_line.append("  "+\
                    readable_hours_range(open_time, close_time))
              
            # add to the readable
            readable.append("".join(processed_line)+"<br/>")
            
            return readable
            
    def _format_input(self):
        """
        create a map with the open and close time as the keys.
        Returns the order and hours_map.
        """
        order, hours_map = [], {}
        for k, v in self.hours.iteritems():
            # v is hours-x-day_y
            if v not in hours_map:
                order.append(v)
                hours_map[v] = []
            if v not in hours_map[v]:
                hours_map[v].append(int(k.split("_")[-1]))
        return order, hours_map
        
        
    def _get_closed_days(self):
        """
        Returns the closed days as a list of integers from 1-7.
        """
        closed_days = range(1, 8)
        
        for k in self.hours.iterkeys():
            day = int(k.split("_")[-1])
            if day in closed_days:
                closed_days.remove(day)
            
            if len(closed_days) == 0:
                break
        
        return closed_days
        
        
    def readable(self):        
        """
        Hours input must be of the format:
        {
            hours-1-day_1: "0600,1330",
            hours-1-day_2: "0600,1330",
            hours-2-day_4: "1530,2330",
            hours-2-day_6: "1530,2330",
            ...
        }
        
        The return value would then be:
        Sundays and Monday - Friday  6:00 AM - 1:30 PM<br/>
        Wednesdays and Fridays  3:30 PM  - 11:30 PM<br/>
        Closed Sundays and Saturdays
        """
        # get the open days readable
        readable = self._to_readable(*self._format_input())
        
        # get the closed days readable
        # just pass in a dummy for order
        closed_days = self._get_closed_days()
        if len(closed_days) > 0:
            readable.append("Closed ")
            readable.extend(self._to_readable(["x"],
                {"x": closed_days}, False))
        
        return "".join(readable)
    
