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
                
def format_geopoint(latitude, longitude):
    """
    Returns the Parse GeoPoint __type or None.
    """
    try:
        return { "__type": "GeoPoint",
                "latitude": float(latitude),
                "longitude": float(longitude) }
    except ValueError:
        return None

def query(constraints, where_only=False):
    """
    Returns the formatted constraints in Parse format.
    Does not yet include Relations. 
    Use parse.core.advanced_queries for Relation queries.
    """
    where, q, ignore = {}, {}, []
    # ignore is a list for keys to skip because it has a partner
    # e.g. createdAt__lte, createdAt__gte
    for key, value in constraints.iteritems():
        # skip key ending with a number greater than 1 ($or)
        if key[-1].isdigit() and int(key[-1]) > 1:
            continue
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

            # compound queries ($or) keys endwith a number TODO
            # currently only supports 1 key to be in the $or
            # only supports regular where params (not date or ptr)
            elif not key.__contains__("__") and\
                key[-1].isdigit() and int(key[-1]) == 1:
                cts, ind = [{key[:-1]:value}], 2
                while True:
                    if key[:-1] + str(ind) not in constraints:
                        break                    
                    cts.append({ key[:-1]:\
                        constraints.get(key[:-1] + str(ind)) })
                    ind += 1
                where["$or"] = cts

            # dates and date built-ins
            elif key in ("createdAt", "updatedAt") or\
                key.startswith("date_"):
                where[key] = format_date(value)
            # GeoPoint
            elif key == "coordinates":
                where[key] = format_geopoint(value[0], value[1])
            # Pointer __type
            elif key[0].isupper() and not key.endswith('_'): 
                where[key] = format_pointer(key, value)
            else:# regular where params
                where[key] = value

    if where_only:
        return where

    q['where'] = json.dumps(where)
    return q
