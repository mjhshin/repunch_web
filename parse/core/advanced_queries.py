"""
Contains somewhat advanced queries not yet supported in ParseObjects.

Example : pointer_query
To get the Subscription objects that have an active store and whose
date_last_charged is greater than date_x and whose subscriptionType
is not free.

The method call is:
pointer_query("Subscription", {subscriptionType1:1,
    subscriptionType2:2, date_last_charged__gte:date_x}, 

Example : relational_query
To get the Punch objects in the relation of a Store object where
the name of the relation is Punches and the store object's
objectID is 4IBEy0cum4. Furthermore, the Punches must have been
created before end-date and after start-date and must have a 
pointer to a Patron whose gender is Female.

The method call is:
relational_query('4IBEy0cum4', 'Store', 'Punches', 'Punch',
    'Patron', 'Patron', {"gender": "Female"},
    {'createdAt__lte':end-date, 'createdAt__gte':start-date} )

"""

import json

from parse.utils import parse
from parse.core.formatter import query

def relational_query(src_id, src_class, src_key, dst_class,
        dst_class_key, dst_class_key_class, dst_class_key_where,
        dst_class_where=None, dst_class_key_where_exclude=False,
        count=False):
    """ 
    Make a query in an object's relation where the query involves
    a pointer to another class.
    
    src_id : the objectId of the of the object in the class in which 
            the relation column exists.
    src_class : the name of the class of the object with the src_id
    src_key : the name of the relation column of the src_class

    dst_class : the output object's class - the class we are querying.
    dst_class_where : append more constraints to the where clause.
    dst_class_key : the name of the column in the dst_class in which
                    the inQuery applies.
    dst_class_key_class : the class name of the dst_class_key
    dst_class_key_where : where parameter of the dst_class_key_class
    dst_class_key_where_exclude : inQuery if false

    count : if True, will only return the count of the results
    """
    if dst_class_key_where_exclude:
        x = "$notInQuery"
    else:
        x = "$inQuery"
    where = {
                # specify the relation (which class contains
                # it and which column is it
                "$relatedTo": {
                    "object": {
                        "__type": "Pointer",
                        "className": src_class,
                        "objectId": src_id
                    },
                    "key": src_key
                }, 
                # this is how queries are done to Pointer types
                dst_class_key:{
                    x:{
                        "where":query(dst_class_key_where,
                                    where_only=True),
                        "className": dst_class_key_class,
                        # inner limit applies!
                        "limit":900, 
                    }
                }      
            }
    if dst_class_where:
        where.update(query(dst_class_where, where_only=True))
    if count:
        res = parse("GET", "classes" + "/" + dst_class, query={
            "where":json.dumps(where), "count":1, "limit":0,
        })
        if 'error' not in res:
            return res['count']
        return None # shall not be 0
    
    return parse("GET", "classes" + "/" + dst_class, query={
            "where":json.dumps(where), 
        })



