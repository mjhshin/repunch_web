"""
Parse models corresponding to Django models
"""
from json import dumps
from importlib import import_module

from parse.utils import parse

NOT_WHERE_CONSTRAINTS = ["include", "count", "limit"]

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
    
    def count(self, **constraints):
        """ returns the number of objects that matches the constraints
        """
        res = parse("GET", self.path + self.pathClassName, query={
                    "where":dumps(constraints),
                    "count":1,"limit":0} )

        if res and 'count' in res:
            return res['count']
        return 0

    def filter(self, **constraints):
        """ returns the list of objects that matches the
        constraints.the class objects.

        See NOT_WHERE_CONSTRAINTS for 
        supported non-object attr constraints
        """
        q = {}
        # separate the "where" parameters from the rest
        for p in NOT_WHERE_CONSTRAINTS:
            q[p] = constraints.pop(p)
        
        q["where"] = dumps(constraints)
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

    Usage Notes
    -----------------------------------------------------------
    ### Initialization:

        The init method of this class must be called in the 
        __init__ method of the subclass with the initial data.
        
        e.g. 
            class Person(ParseObject):
                def __init__(self, data={})
                    # regular type
                    self.name = data.get("name")
                    # Date type
                    self.date_born = data.get("date_born")
                    # Pointer type
                    self.Mother = date.get("Mother")
                    # Relation type
                    self.Friends_ = "Person"

                    super(Person, self).__init__()

        -------------------------------

    Supported Data Types
    -----------------------------------------------------------
    ### Pointers:

        Pointers are attributes whose first character is upper-cased.
 
            e.g. self.MilkyWay

        These attributes should store an objectId. 
        The name of the attribute is used as the column name in Parse.

        A cache attribute is created that contains the actual 
        ParseObject (initially None) that it points to.
        The cache attribute name is the Pointer name with the first
        character lowercased.
            e.g. self.milkyWay
        To get the actual object:
            e.g. self.get("milkyWay")
        -------------------------------

    ### Relations:

        Relations are attributes whose first character is 
        upper-cased and ends with and underscore.

            e.g. self.MilkyWay_

        These attributes should store the name of the class is
        stored in the relation and should not be modified.
        The name of the attribute is used as the column name in Parse.

        A cache attribute is created that contains the actual list of
        ParseObjects (initially None) that it contains.
        The cache attribute name is the Relation name with the first
        character lowercased and the underscore at the end stripped.

            e.g. self.milkyWay

        To get the actual list of objects:

            e.g. self.get("milkyWay")

        -------------------------------

    ### Dates:
        
        Dates are attributes whose name starts with date_.
        These attributes needs to contain a UTC timestamp stored in
        ISO 8601 format.
        
        e.g. 
            from datetime import datetime
            self.set("date_born", datetime.today().isoformat())

        -------------------------------

    Instance Methods
    -----------------------------------------------------------
    ### self.get(attr)
        
        All class attributes values should be obtained using this
        method. However, objectId, createdAt, updatedAt may
        be accessed without having to use this method.
        
        -------------------------------

    ### self.set(attr, value)

        Sets the value of the attribute to the given value.

        -------------------------------

    ### self.update()

        Updates the data in the Parse DB with this object's values.
        Cache attributes are not pushed up and are set to None.
        However, for Pointers, the cache attributes are only set to
        None if the Pointer's objectId has changed.
    
        -------------------------------

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

        self._generate_cache_attrs()
        self.update_locally(data)

    def _generate_cache_attrs(self):
        """ 
        create the cache attrs for the Pointers and Relations if any.
        """
        for attr in self.__dict__:
            # Relations
            if attr[0].isupper() and attr.endswith("_"):
                setattr(self, attr[0].lower() + attr[1:-1] , None)
            elif attr[0].isupper() and not attr.endswith("_"):
                setattr(self, attr[0].lower() + attr[1:] , None)

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
        # get the formated data to be put in the request
        data = self._get_formatted_data()

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
        data = self._get_formatted_data()
        
        if res and "error" not in res:
            self.update_locally(res)
            return True
        
        return False

    def delete(self):
        """ delete the row corresponding to this object in Parse """
        # TODO 
        pass


    ### "Private" methods
    def _get_formatted_data(self):
        """ 
        returns a dictionary to be used in a PUT request for Parse.

        Relations, Relation caches, 
        and Pointer caches are not included.
        """
        data = {}
        for key, value in self.__dict__.iteritems():
            # exclude Relation attrs
            if key.endswith("_"):
                continue
            # exclude Relation caches and clear it
            if key[0].islower() and\
                key[0].upper() + key[1:] + "_" in self.__dict__:
                self.__dict__[key] = None
                continue
            # exclude the Pointer cache and maybe clear it
            if  key[0].islower() and\
                (key[0].upper() + key[1:] in self.__dict__):
                # clear the cache objects if their pointers changed
                if value and value.objectId !=\
                    self.__dict__[key[0].upper() + key[1:]]:
                    self.__dict__[key] = None
                continue

            # Pointers
            if key[0].isupper() and not key.endswith("_"):
                data[key] = {
                    "__type": "Pointer",
                    "className": key,
                    "objectId": value
                }
            # Dates
            elif key.startswith("date_"):
                data[key] = {
                    "__type": "Date",
                    "iso": value
                }
            # regular attributes
            else:
                data[key] = value

        return data

