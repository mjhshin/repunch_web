"""
Contains somewhat advanced queries not yet supported in ParseObjects.

Example : relational_query
To get the Punch objects in the relation of a Store object where
the name of the relation is Punches and the store object's
objectID is 4IBEy0cum4. Furthermore, the Punches must have a 
pointer to a Patron whose gender is Female.

The method call is:
relational_query('4IBEy0cum4', 'Store', 'Punches', 'Punch',
    'Patron', 'Patron', {"gender": "Female"} )

"""

import json

from parse.utils import parse

def relational_query(src_id, src_class, src_key, dst_class,
        dst_class_key, dst_class_key_class, dst_class_key_where,
        dst_class_key_where_exclude=False):
    """ 
    Make a query in an object's relation where the query involves
    a pointer to another class.
    
    src_id : the objectId of the of the object in the class in which 
            the relation column exists.
    src_class : the name of the class of the object with the src_id
    src_key : the name of the relation column of the src_class

    dst_class : the output object's class - the class we are querying.
    dst_class_key : the name of the column in the dst_class in which
                    the inQuery applies.
    dst_class_key_class : the class name of the dst_class_key
    dst_class_key_where : where parameter of the dst_class_key_class
    dst_class_key_where_exclude : inQuery if false
    """
    if dst_class_key_where_exclude:
        x = "$notInQuery"
    else:
        x = "$inQuery"
    return parse("GET", "classes" + "/" + dst_class, query={
            "where":json.dumps({
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
                # this how queries are done to Pointer types
                dst_class_key:{
                    x:{
                        "where":dst_class_key_where,
                        "className": dst_class_key_class,
                    }
                }      
            }), # end where
        }) # end parse



