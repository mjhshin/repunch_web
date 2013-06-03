"""
Format python objects to Parse objects, which are dictionaries.
"""

import json
from dateutil import parser

from repunch.settings import USER_CLASS

NOT_WHERE_CONSTRAINTS = [
    "include", "count", "limit", "order"
]

WHERE_OPTIONS = [
    "lt", "lte", "gt", "gte", 
]

def format_date(dateObj):
    """
    Returns the Parse Date __type of the given
    datetime.date or datetime.datetime object or None.
    """
    if dateObj:
        return { "__type": "Date",
          "iso": parser.parse(dateObj.isoformat()).isoformat() }

def format_pointer(className, objectId):
    """
    Returns the Parse Pointer __type or None.
    """
    if className == USER_CLASS:
        tmp = "_User"
    else:
        tmp = className
    if objectId:
        return { "__type": "Pointer",
                "className": tmp,
                "objectId": objectId }

def format_file(name):
    """
    Returns the Parse File __type or None.
    """
    if name:
        return { "__type": "File",
                "name": name }

def query(constraints):
    """
    Returns the formatted constraints in Parse format.
    """
    where, q = {}, {}
    for key, value in constraints.iteritems():
        if key in NOT_WHERE_CONSTRAINTS:
            q[key] = value
    
        else:
            # where options TODO spanning tables
            if key.__contains__("__"):
                args = key.split("__")
                if len(args) == 2 and args[1] in WHERE_OPTIONS:
                    if args[0].__contains__("date_"):
                        where[key] = {
                            "$" + args[1]: format_date(value)
                        }
            # Pointer __type
            elif key[0].isupper() and not key.endswith('_'): 
                where[key] = format_pointer(key, value)
            else:# regular where params
                where[key] = value

    q['where'] = json.dumps(where)
    return q
