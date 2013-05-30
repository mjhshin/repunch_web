"""
Parse models corresponding to Django models
"""
from json import dumps
from importlib import import_module

from parse.utils import parse

class ParseObjectManager(object):
    """
    Provides extra methods for ParseObjects such as counting.
    This provides functionality similar to Django's Model.objects
    """
    def __init__(self, path, pathClassName, className, module):
        self.path = path
        self.pathClassName = pathClassName
        self.className = className
        self.module = module
    
    def count(self, **params):
        """ returns the number of objects that matches the
        filter parameters in params
        """
        res = parse("GET", self.path + self.pathClassName, query={
                    "where":dumps(params),
                    "count":1,"limit":0} )

        if res and 'count' in res:
            return res['count']
        return 0

    def filter(self, **params):
        """ returns the list of objects that matches the
        filter parameters in params. This can be used to get all
        the class objects.
        """
        q = {}
        # separate the "where" parameters from the rest
        if "limit" in params:
            q["limit"] = params.pop("limit")
        if "order" in params:
            q["order"] = params.pop("order")
        
        q["where"] = dumps(params)
        res = parse("GET", self.path + self.pathClassName, query=q)
                  
        if res and "results" in res:
            objClass = getattr(import_module(self.module), 
                                self.className)
            objs = []
            for data in res['results']:
                objs.append(objClass(data))     
            return objs
        
        return None

class ParseObject(object):
    """ Provides a Parse version of the Django models 
    This class is abstract and no concrete objects should be
    created using this class.

    Rules:
        1. If the first letter of an attribute is capitalized, then
            it is treated as a Pointer. If the first letter of an
            attribute is capitalized and it endswith an 
            underscore then it is a Relation.
            A Pointer attr may be None or contain an objectId.
            A Relation is a constant string, which is the name of
            the class that will be stored in the relation.

        1.1 To get the object of a Pointer, use it's cache attr.
            To get the objects of a Relation, use it's cache attr.

        1.2 The attr name of the Pointers and Relations are used
            for the column name in the Parse DB (excluding _
            at the end of each Relation attr.

        2. If the first letter of an lower case and there exist a #1
            matching the attr if its first char is capitalized 
            (plus an _ at the end if it is a Relation), 
            then the attr will not be saved to Parse.
            This can be used as a cache.
            A cache for a Pointer contains None or a ParseObject.
            A cache for a Relation contains None or a list of
            ParseObjects, which only contain their objectIds.
           
        2.5 Also, the value of a Relation attr is not pushed up.
            Use add_relations for Relations.

        3. the init method of this class must be called in the 
            __init__ method of the subclass with the initial data

        4. use the get(self, attr) method to get an attribute.
            Do not reference the attrs directly by using a dot UNLESS
            the attribute is objectId, createdAt, or updatedAt.
    """
    
    # initialize the manager for a class
    # must be overriden by the ParseObject that will be used as the
    # User class in Parse DB

    @classmethod
    def objects(cls):
        if not hasattr(cls, "_manager"):
            setattr(cls, "_manager", ParseObjectManager('classes/',
                    cls.__name__,  cls.__name__, cls.__module__))
        return cls._manager

    def __init__(self, data={}):
        self.objectId = data.get('objectId')
        self.createdAt = data.get('createdAt')
        self.updatedAt = data.get('updateAt')
        self.update_locally(data)

    def path(self):
        """ returns the path of this class or use with parse 
        returns classes/ClassName
        """
        return "classes/" + self.__class__.__name__

    def update_locally(self, data):
        """
        Replaces values of matching attributes in data
        capitalized attributes only store an objectId.
        """
        for key, value in data.iteritems():
            # make sure Relation vals are untouched
            if key.endswith("_"):
                continue
            if key in self.__dict__.iterkeys():
                if key[0].isupper() and type(value) is dict:
                    self.__dict__[key] = value.get('objectId')
                else:
                    self.__dict__[key] = value

    def get_class(self, className):
        """
        Need to override this for every class in order to use caching.
        Returns the class with the className.
        TODO Automate this process?
        """
        return None

    def get(self, attr):
        """ returns attr if it is not None, otherwise fetches the 
        attr from the Parse DB and returns that. 

        If the attr is a #2, then it is treated
        as a cache for a ParseObject. Note that all of this 
        attribute's data is retrieved.
        """    
        if attr not in self.__dict__:
            return None
        if self.__dict__.get(attr):
            return self.__dict__.get(attr)

        # Pointer cache
        if attr[0].islower() and\
                    attr[0].upper() + attr[1:] in self.__dict__:
                className = attr[0].upper() + attr[1:]
                res = parse("GET", "classes/" + className +\
                        "/" + self.__dict__.get(className))
                if res and "error" not in res:
                    c = self.get_class(className)
                    self.__dict__[attr] = c(res)
                else:
                    return None

        # Relation cache
        elif attr[0].islower() and attr[0].upper() + attr[1:] +\
                "_" in self.__dict__:
            className = self.__dic__[attr[0].upper() + attr[1:] + "_"]
            relName = attr[0].upper() + attr[1:]
            res = parse("GET", 'classes/' + className, query={
                    "where":json.dumps({
                        "$relatedTo":{ 
                        "object":{
                            "__type": "Pointer",
                            "className": self.__class__.__name__,
                            "objectId": self.objectId},
                        "key": relName, }  })  })
            if res and "error" not in res:
                c = self.get_class(className)
                self.__dic__[attr] = [ c(d) for d in res['results'] ]
            else:
                return None 
        # attr is a regular attr
        else: 
            res = parse("GET", self.path(), query={"keys":attr})
            self.update_locally(res.get('results')[0])

        return self.__dict__[attr]

    def set(self, attr, val):
        """ set this object's attr to val. This does not commit
        anything up to Parse. """
        self.__dict__[attr] = val

    def add_relation(self, relAttrName, objectIds):
        """ Adds the list of objectIds to the given relation. 
        relAttrName is a str, which is the name of the Relation attr.

        Adds the relations to Parse and empty  the cache. 
        Returns True if successful.
        """
        if relAttrName not in self.__dict__:
            return False
        objs = []
        for oid in objectIds:
            objs.append( { "__type": "Pointer",
                           "className": self.__dict__[relAttrName],
                           "objectId": oid } )
        res = parse("PUT", self.path() + "/" + self.objectId, {
                    relAttrName[:-1]: {
                        "__op": "AddRelation",
                        "objects": objs, 
                    }
                 } )
        if res and 'error' not in res:
            cacheAttrName = relAttrName[0].lower() + relAttrName[1:-1]
            self.__dic__[cacheAttrName] = None
            return True
        else:
            return False

    def update(self):
        """ Save changes to this object to the Parse DB.
        Returns True if update is successful. 
        
        Handles Pointers to other objects. If the pointer changed,
        then the cache corresponding to the attr is set to None.
        Relations are not handled by update. Use add_relation
        for Relations.
        """
        # exclude cache attrs
        data = self._exclude_attrs()
        
        rels = self._get_pointers()
        if rels:
            for key, value in rels.iteritems():
                data[key] = value

        res = parse("PUT", self.path() + "/" + self.objectId, data)
        if res and "error" not in res:
            self.update_locally(res)
            return True

        return False

    def create(self):
        """ 
        creates this object to the DB. This does not check 
        uniqueness of any field. 
        Use update to save an existing object.

        After a successful request, this object will now have the
        objectId available but not the rest of its attributes. 

        Note that self.__dict__ contains objectId which will result
        to the parse request returning an error only if it is not None

        If there exist a Pointer to other objects,
        this method makes sure that it is saved as a Pointer.
        """
        data = self._exclude_attrs()
        rels = self._get_pointers()
        if rels:
            for key, value in rels.iteritems():
                data[key] = value
        res = parse('POST', self.path(), data)
        
        if res and "error" not in res:
            self.update_locally(res)
            return True
        
        return False

    def delete(self):
        """ delete the row corresponding to this object in Parse """
        # TODO 
        pass


    ### "Private" methods
    def _get_pointers(self):
        """
        Returns a dictionary of relations of this class.
        An attribute is a Pointer if the first character is
        capitalized. 

        Note that this only handles Pointers. Use add_relations
        for relations.
        """
        pointers, data = [], {}

        # pointers will now contain a list of tuples 
        # (className, objectId)
        for key, value in self.__dict__.iteritems():
            if key[0].isupper() and not key.endswith("_"):
                pointers.append( (key, value) )
            
        # populate the data in proper format
        if pointers:
            for pointer in pointers:
                data[pointer[0]] = {
                    "__type": "Pointer",
                    "className": pointer[0],
                    "objectId": pointer[1]
                }

        return data

    def _exclude_attrs(self):
        """ returns a dictionary containing all the keys and values
        in self.__dict__ that are not used for caching and not 
        a relation. """
        data = {}
        for key, value in self.__dict__.iteritems():
            # exclude the Relation attr and its cache attr
            if key.endswith("_") or (key[0].islower() and\
                key[0].upper() + key[1:] + "_" in self.__dict__):
                continue
            # exclude the Pointer cache
            if  key[0].islower() and\
                (key[0].upper() + key[1:] in self.__dict__):
                # clear the cache objects if their pointers changed
                if value and value.objectId !=\
                    self.__dict__[key[0].upper() + key[1:]]:
                    self.__dict__[key[0].upper() + key[1:]] = None
                continue
            data[key] = value
        return data

