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
    "lt", "lte", "gt", "gte", "in", "nin",
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

def query(constraints, where_only=False):
    """
    Returns the formatted constraints in Parse format.
    """
    where, q, ignore = {}, {}, []
    # ignore is a list for keys to skip because it has a partner
    # e.g. createdAt__lte, createdAt__gte
    for key, value in constraints.iteritems():
        if key in ignore:
            continue
        if key in NOT_WHERE_CONSTRAINTS:
            q[key] = value
    
        else:
            # where options TODO spanning tables
            if key.__contains__("__"):
                args = key.split("__")
                if len(args) == 2 and args[1] in WHERE_OPTIONS:
                    # done this way to take care of 
                    # 2 or more constraint on same attr
                    inner = {}
                    for k, v in constraints.iteritems():
                        if args[0] != k and\
                        k.startswith(args[0]) and\
                        k.__contains__("__"):
                            gs = k.split("__")
                            ignore.append(k)
                            # date 2 or more constraints
                            if gs[0].__contains__("date_") or\
                                gs[0] in ("createdAt", "updatedAt"):
                                inner.update({"$" + gs[1]:\
                                        format_date(v)})
                            else:
                                inner.update({"$" + gs[1]:v})
                    # date 1 constraint
                    if args[0].__contains__("date_") or\
                        args[0] in ("createdAt", "updatedAt"):
                        inner.update({"$" + args[1]:\
                                format_date(value)})
                    else: 
                        inner.update({"$" + args[1]: value})
                    where.update({args[0]:inner})
            # dates built-ins
            elif key in ("createdAt", "updatedAt") or\
                key.startswith("date_"):
                where[key] = format_date(value)
            # Pointer __type
            elif key[0].isupper() and not key.endswith('_'): 
                where[key] = format_pointer(key, value)
            else:# regular where params
                where[key] = value

    if where_only:
        return where

    q['where'] = json.dumps(where)
    return q
