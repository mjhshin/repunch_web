"""
Hours interpreter re-written.
"""

from parse.apps.stores import models

import types

class HoursInterpreter:
    def __init__(self, hours=[]):
        self._hours = hours
        self._closed = range(1,8)
        
    def _open(self, day):
        if self._closed.count(day) > 0:
            self._closed.remove(day)
            
    #converts the list of days to an easy iterable array that will provide the correct
    #format for the days of the week
    def _pack_days(self, days):
        packed = []
        for day in days:
            self._open(day)
                
            if len(packed) == 0:
                packed.append(day)
            else:
                last = packed[-1]
                if isinstance(last, types.TupleType): # if this is a tuple then we creating a series and see if we need to add to it
                    last_day = last[1]
                    if last_day+1 == day:
                        packed[-1] = (last[0], day)
                    else:
                        packed.append(day) #not part of the series so continue
                else: #then it is a number
                    if last+1 == day:
                        packed[-1] = (last, day)
                    else:
                        packed.append(day)  
        # end for days
        
        #loop through and if there are only 2 consecutive days, pull them out
        for pack in packed:
            if isinstance(pack, types.TupleType):
                if pack[1]-pack[0] == 1:
                    index = packed.index(pack)
                    packed[index] = pack[0]
                    packed.insert(index+1, pack[1])
        
        return packed
    
    def _to_readable(self, day, prefix=None, separator=None, postfix=None, day_names=models.SHORT_DAYS):
        rv = []
        if prefix != None:
            rv.append(prefix)
        
        if isinstance(day, types.TupleType):
            rv.append(day_names[day[0]-1][1])
            if separator != None:
                rv.append(separator)
            rv.append(day_names[day[1]-1][1])
        else:
            rv.append(day_names[day-1][1])
            
        if postfix != None:
            rv.append(postfix)
            
        return rv;
        
    def _to_readable_days(self, packed_days):
        description = []
        
        if len(packed_days) == 2 and not isinstance(packed_days[0], types.TupleType) and not isinstance(packed_days[1], types.TupleType) :
            description.extend(self._to_readable(packed_days[0], postfix='s and ', day_names=models.DAYS))
            description.extend(self._to_readable(packed_days[1], postfix='s', day_names=models.DAYS))
            
        elif len(packed_days) > 1:
            for pack in packed_days[:-1]:     
                description.extend(self._to_readable(pack, separator=' - ', postfix=', '))
                       
            description.pop()
            # append the last one
            description.extend(self._to_readable(packed_days[-1], separator=' - ', prefix=' and '))
            
        else:
            pack = packed_days[0]
            description.extend(self._to_readable(pack, day_names=models.DAYS, separator=' - '))
            if not isinstance(pack, types.TupleType):
                description.append('s')
                
        return description
        
    def readable(self):        
        rv = []
        for hour in self._hours:
            
            if len(hour.days) == 0:
                continue
            
            days = []
            for x in hour.days:
                if len(x) > 0:
                    days.append(int(x))  #change to to work easier
            
            if(len(days) == 0):
                continue
            
            packed = self._pack_days(days)
            
            
            description = self._to_readable_days(packed)
            description.extend(('&nbsp;&nbsp;',
                                hour.open.strftime('%I:%M %p ').lstrip('0'), ' - ',
                                hour.close.strftime('%I:%M %p ').lstrip('0'), '<br/>'))
            
            rv.extend(''.join(description))
        
        if len(self._closed) > 0:
            rv.append("Closed ")
            
            closed = list(self._closed) #need a copy
            packed = self._pack_days(closed)
            rv.extend(self._to_readable_days(packed))
        
        return ''.join(rv)
    
