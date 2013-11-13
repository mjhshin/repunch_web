"""
Hours interpreter re-written.
"""

from apps.stores.models import DAYS, SHORT_DAYS
from parse.apps.stores import models

SPACE = "&nbsp;"

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
        return SPACE+"and"+SPACE.join(d)
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
    
def get_lexicographical_time(time):
    """
    The day "starts" from 0600 and ends at 0530.
    This returns an integer representing the given time 
    lexicographically from 0600 to 0530.
    0600 = 0
    0630 = 1
    ...
    0500 = 46
    0530 = 47
    """
    hour, minute = int(time[:2]), int(time[2:])
    # normal time starts from 0000 = 0 to 2330 = 47
    # 0600 would be 12 normal time so we just need to shift everything by 12
    index = (hour*2) + (minute/30) - 12
    if index < 0: # these are times 0530 and below
        index += 48
    
    return index
            
class HoursInterpreter:
    """
    Transforms store_edit.js inputs and Parse formatted hours to readable
    and also provides hours validation.
    """

    def __init__(self, hours):
        self.hours = hours
        
    def is_valid(self):
        """
        Returns True if the following conditions are met:
            1. hours must not overlap
            2. if open time is greater than close time, then close time
               must be earlier than or equal to 5.30 am.
            3. allDayBit (from _format_javascript_input) must be 1 if
                open time is equal to close time. Otherwise, the user 
                manually entered the same open and close time w/o
                checking the 24 hours / allDay checkbox.
               
        Close time and open time being equal is valid.
        This is only used to validate javascript input - not Parse hours,
        which will always be valid.
        """
        order, hours_map = self._format_javascript_input(True)
        # At this point we have something like the below.
        # 
        # hours_map = {
        #     ("0600", "1330"): [1,2],
        #     ("1530", "1530"): [4,6],
        # }
        # 
        # order = {
        #     1: ("0600", "1330", "0"),
        #     2: ("1530", "1530", "1"), # valid since third bit is "1"
        # }
        order_list, days_map = [ i for i in order.keys() ], {}
        order_list.sort() # order doesn't really matter but whatever
        
        def hours_overlap(time, days):
            """
            Check if this hours has a conflict with an hours in
            the days_map. This does not handle open time being the
            same as close time.
            
            days_map = {
                1: [("0600", "1330", "0"), ...],
                2: [("0600", "1330", "0"), ...],
                4: [("1530", "1530", "1"), ...],
                6: [("1530", "1530", "1"), ...],
            }
            """
            open_time, close_time = time[:2]
            open_time = get_lexicographical_time(open_time)
            close_time = get_lexicographical_time(close_time)
            
            for day in days:
                if day not in days_map:
                    days_map[day] = []
                    
                # check hours the day after if the open = close
                # close_time has to be <= tomorrow's opening
                if open_time == close_time:
                    next_day = day + 1
                    if next_day == 8:
                        next_day = 1
                    hours_tomorrow = days_map.get(next_day, [])
                    for hours in hours_tomorrow:
                        open = get_lexicographical_time(hours[0])
                        if close_time > open:
                            return True
                            
                # check hours the day before
                prev_day = day - 1
                if prev_day == 0:
                    prev_day = 1
                hours_yesterday = days_map.get(prev_day, [])
                for hours in hours_yesterday:
                    open, close = hours[:2]
                    open = get_lexicographical_time(open)
                    close = get_lexicographical_time(close)
                    # overlap may only occur if yesterday is 24 hours
                    if open == close and open_time < close:
                        return True
                
                # check hours on the same day
                hours_today = days_map[day]
                for hours in hours_today:
                    open, close = hours[:2]
                    open = get_lexicographical_time(open)
                    close = get_lexicographical_time(close)
                    if open == close:
                        if close_time == open_time or close_time > open:
                            # close_time has to be <= todays's opening
                            return True
                    else:
                        if close_time == open_time and open_time < close:
                            return True
                            
                        elif close_time != open_time:
                            if not ((open_time < open and\
                                close_time <= open) or\
                                (open_time >= close and\
                                close_time > close)):
                                return True
            
                # all valid - add the hours to the days map
                days_map[day].append(time)
                
            return False
        
        for i in order_list:
            time, days = order[i], hours_map[order[i]]
            open_time, close_time, all_day = time
            open_time = get_lexicographical_time(open_time)
            close_time = get_lexicographical_time(close_time)
            
            # condition 2
            # The comparison uses lexicographical ordering *1*
            if open_time > close_time:
                return "The opening time cannot be later than the "+\
                    "closing time."
            # condition 3
            if open_time == close_time and all_day == "0":
                return "The opening time cannot be the same as the "+\
                    "closing time."
            
            # Here comes the hard part - condition 1
            if hours_overlap(time, days):
                return "The store hours cannot overlap."
        
        return True
        
    def from_javascript_to_parse(self):
        """
        Transforms javascript input to Parse hours format.
        Example input:
        {
            hours-1-day_1: "0600,1330",
            hours-2-day_6: "1530,2330",
            ...
        }
        
        Output would then be:
        [
            {
                day: 1,
                open_time: "0600",
                close_time: "1330"
            },
            {
                day: 6,
                open_time: "1530",
                close_time: "2330"
            }
        ]
        """
        # first merge same (open, close) together
        order, hours_map = self._format_javascript_input()
        formatted = []
        
        # sort the order
        order_list = [ i for i in order.keys() ]
        order_list.sort()
        """
        hours_map = {
            ("0600", "1330"): [1,2],
        }
        """
        for i in order_list:
            key, days = order[i], hours_map[order[i]]
            for day in days:
                formatted.append({
                    "day": day,
                    "open_time": key[0],
                    "close_time": key[1],
                })
        
        return formatted
        
    def _to_readable(self, order, hours_map, open=True):
        readable = []
        
        # sort the order
        order_list = [ i for i in order.keys() ] 
        order_list.sort()
        
        # keep the order of the hours and process each set of open
        # and close time
        for i in order_list:
            k = order[i]
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
            names, line = DAYS, []
            if len(solos) > 2 or len(groups) > 1 or len(solos) +\
                len(groups) > 2:
                names = SHORT_DAYS
            
            # make readable grouped days
            while len(groups) > 0:
                group = groups.pop(0)
                start, end = min(group), max(group)
                
                # case that there is a gap in b/w the min and max
                # e.g 1,2,5,6,7
                if set(group) != set(range(start, end+1)): 
                    # find the left most day from the max before gap
                    while True:
                        if end - 1 not in group:
                            break;
                        end-=1
                    # find the right most day from the min before gap
                    while True:
                        if start + 1 not in group:
                            break;
                        start+=1
                        
                    # swap 
                    tmp = start
                    start = end
                    end = tmp 
                
                # add the groups to the line if any     
                line.append(names[start-1][1]+SPACE+"-"+SPACE+names[end-1][1])
                
            # add the solo days to the line if any
            line.extend(readable_days_list(solos, list, names))
                
            # time to add separators
            total, processed_line = len(line), []
            if total > 2: # commas + and
                for l in line:
                    if line.index(l) == total - 1: # last element
                        processed_line.append("and"+SPACE)
                        processed_line.append(l)
                    else:
                        processed_line.append(l)
                        processed_line.append(","+SPACE)
                     
            elif total == 2: # and
                processed_line.append(line[0])
                processed_line.append(SPACE+"and"+SPACE)
                processed_line.append(line[1])
            else: # just 1 element
                processed_line = line
            
            # add the close and open time to the line
            # if these days are open
            if open:
                open_time, close_time = k
                processed_line.append(SPACE*4+\
                    readable_hours_range(open_time, close_time))
                # if open is the same as close it is 24 hours
                if open_time == close_time:
                    processed_line.append(SPACE+"(Open 24 hours)")
              
            # add to the readable
            readable.append("".join(processed_line)+"<br/>")
            
        return readable
            
    def _format_parse_input(self):
        """
        Returns the order and hours_map used for _to_readable.
        
        Example input:
        [
            {
                day:1,
                open_time: "0600",
                close_time: "1330",
            }, 
            {
                day:2,
                open_time: "0600",
                close_time: "1330",
            }, 
            ...
        ]
        
        Output would then be:
        hours_map = {
            ("0600", "1330"): [1,2],
        }
        order = {
            1: ("0600", "1330"),
        }
        """
        order, hours_map = {}, {}
        for i, hour in enumerate(self.hours):
            key = (hour["open_time"], hour["close_time"])
            day = hour["day"]
            if key not in hours_map:
                order.update({ i: key })
                hours_map[key] = []
            if day not in hours_map[key]:
                hours_map[key].append(day)
        return order, hours_map
        
            
    def _format_javascript_input(self, allDayBit=False):
        """
        Returns the order and hours_map used for _to_readable.
        
        Example input:
        {
            hours-1-day_1: "0600,1330",
            hours-1-day_2: "0600,1330",
            hours-2-day_4: "1530,2330",
            hours-2-day_6: "1530,2330",
            ...
        }
        
        Output would then be:
        hours_map = {
            ("0600", "1330"): [1,2],
            ("1530", "2330"): [4,6],
        }
        
        order = {
            1: ("0600", "1330"),
            2: ("1530", "2330")
        }
        
        If allDayBit is True then the key would b a 3-tuple.
        From ("0600", "1330") to ("0600", "1330", "0|1").
        If allDayBit is True the output of this should not be used
        for _to_readable. Only use it for validation.
        """
        order, hours_map = {}, {}
        for k, v in self.hours.iteritems():
            if allDayBit:
                key = tuple(v.split(","))
            else:
                key = tuple(v.split(",")[:2])
            day = int(k.split("_")[-1])
            if key not in hours_map:
                order.update({ int(k.split("-")[1]): key })
                hours_map[key] = []
            if day not in hours_map[key]:
                hours_map[key].append(day)
        return order, hours_map
        
        
    def _get_parse_closed_days(self):
        """
        Returns the closed days as a list of integers from 1-7.
        
        Example input:
        [
            {
                day:1,
                open_time: "0600",
                close_time: "1330",
            }, 
            {
                day:2,
                open_time: "0600",
                close_time: "1330",
            }, 
            ...
        ]
        Output would then be:
        [ 3, 4, 5, 6, 7 ]
        """
        closed_days = range(1, 8)
        
        for hours in self.hours:
            if hours["day"] in closed_days:
                closed_days.remove(hours["day"])
                
            if len(closed_days) == 0:
                break
        
        return closed_days
        
    def _get_javascript_closed_days(self):
        """
        Returns the closed days as a list of integers from 1-7.
        
        Example input:
        {
            hours-1-day_1: "0600,1330",
            hours-1-day_2: "0600,1330",
            hours-2-day_4: "1530,2330",
            hours-2-day_6: "1530,2330",
            ...
        }
        Output would then be:
        [ 3, 5, 7 ]
        """
        closed_days = range(1, 8)
        
        for k in self.hours.iterkeys():
            day = int(k.split("_")[-1])
            if day in closed_days:
                closed_days.remove(day)
            
            if len(closed_days) == 0:
                break
        
        return closed_days
        
    def from_parse_to_readable(self):        
        """
        Hours input must be of the format:
        [
            {
                day:1,
                open_time: "0600",
                close_time: "1330",
            }, 
            {
                day:2,
                open_time: "0600",
                close_time: "1330",
            }, 
            ...
        ]
        
        The return value would then be:
        Sundays and Monday - Friday  6:00 AM - 1:30 PM<br/>
        Closed Tuesday - Saturday
        """
        # get the open days readable
        readable = self._to_readable(*self._format_parse_input())
        
        # get the closed days readable
        # just pass in a dummy for order
        closed_days = self._get_parse_closed_days()
        if len(closed_days) > 0:
            readable.append("Closed ")
            readable.extend(self._to_readable({1:"x"},
                {"x": closed_days}, False))
        
        return "".join(readable)
    
        
    def from_javascript_to_readable(self):        
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
        Closed Tues, Thurs, and Sat
        """
        # get the open days readable
        readable = self._to_readable(*self._format_javascript_input())
        
        # get the closed days readable
        # just pass in a dummy for order
        closed_days = self._get_javascript_closed_days()
        if len(closed_days) > 0:
            readable.append("Closed"+SPACE)
            readable.extend(self._to_readable({1:"x"},
                {"x": closed_days}, False))
        
        return "".join(readable)
  
  
### FOOTNOTES
# *1* http://docs.python.org/2/tutorial/datastructures.html#comparing-sequences-and-other-types  
