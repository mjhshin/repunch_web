"""
Parse models corresponding to Django models.
"""
from json import dumps
from dateutil import parser
from importlib import import_module

from repunch.settings import USER_CLASS
from parse.utils import parse
from parse.core.formatter import query,\
format_date, format_pointer, format_file, format_geopoint,\
NOT_WHERE_CONSTRAINTS

JSONIFIABLE_TYPES = (int, bool, float, long, str, unicode, list, 
                    dict, tuple)
                    
# avatar is here for backwards compatibility
IMAGE_DELIMITERS = ("avatar", "image")

def is_image(attr_name):
    for delim in IMAGE_DELIMITERS:
        if delim in attr_name:
            return True
    
    return False
                    
# This is to support creating objects from within objects.
# Register all classes here.
GET_CLASS = {
    "parse.apps.stores.models": (
        "Store", "StoreLocation", "Invoice", "Subscription", "Settings",
    ),
    "parse.apps.patrons.models": (
        "Patron", "PatronStore", "PunchCode", "FacebookPost",
    ),
    "parse.apps.messages.models": (
        "Message", "MessageStatus",
    ),
    "parse.apps.rewards.models": (
        "Punch", "RedeemReward",
    ),
    "parse.apps.accounts.models": (
        "Account",
    ),
    "parse.apps.employees.models": (
        "Employee",
    ),
}


def get_class(className):
    """
    Enables retrieval of classes from within classes.
    """
    for pkg, models in GET_CLASS.iteritems():
        for model in models:
            if model == className:
                return getattr(import_module(pkg), className)

class ParseObjectManager(object):
    """
    Provides extra methods for ParseObjects such as counting.
    This provides functionality similar to Django's Model.objects
    """

    def __init__(self, cls):
        if cls.__name__ == USER_CLASS:
            self.path = 'classes/' + "_User"
        else:
            self.path = 'classes/' + cls.__name__
        self.cls = cls
    
    def count(self, **constraints):
        """ 
        returns the number of objects that matches the constraints
        """
        constraints["count"] = 1
        constraints["limit"] = 0
        res = parse("GET", self.path, query=query(constraints) )

        if res and 'count' in res:
            return res['count']

        return 0

    def create(self, **data):
        """ Creates a ParseObject and returns it. """
        obj = self.cls(**data)
        obj.create()
        return obj

    def get(self, **constraints):
        """
        Returns the first result returned by filter if any.
        """
        res = self.filter(**constraints)
        if len(res) > 0:
            return res[0]

    def filter(self, **constraints):
        """ 
        Returns the list of objects that matches the constraints.
        
        See WHERE_OPTIONS for all currently supported options.
        Double underscores allow for usage of WHERE_OPTIONS like 
        gte (greater than or equal to). 
        """
        res = parse("GET", self.path, query=query(constraints))

        if res and "results" in res:
            objs = []
            for data in res['results']:
                objs.append(self.cls(**data))     
            return objs
        
        return [] 

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
                def __init__(self, **data)
                    # regular type
                    self.name = data.get("name")
                    # Date type
                    self.date_born = data.get("date_born")
                    # Pointer type
                    self.Mother = data.get("Mother")
                    # Relation type
                    self.Friends_ = "Person"

                    super(Person, self).__init__(False, **data)

        -------------------------------

    Supported Data Types
    -----------------------------------------------------------
    ### Pointers:

        Pointers are attributes whose first character is upper-cased.
 
            e.g. self.MilkyWay

        These attributes to the objectId of the object it points to.
        The name of the attribute is used as the column name in Parse.

        A cache attribute is created that contains the actual 
        ParseObject (initially None) that it points to.
        The cache attribute name is the Pointer name with the first
        character lowercased. To get the actual object:
            e.g. self.get("milkyWay")

        A pointer may also have a meta attribute which will not be saved.
        This meta is a constant and may be provided if the class name of
        the pointer is not the same as the pointer name.
        Pointer meta attributes startswith _ and are all lower case.

            e.g. If MilkyWay is not the class name, but rather Planet
                self._milkyway = "Planet"

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

    ### Array of Pointers:

        In addition to arrays containing non-relational data-types,
        arrays may also contain actual objects. You must provide a 
        meta attribute to indicate that it is an array of pointers. 
        The value of the meta attribute does not matter.
        
            e.g. the meta attribute of self.array_of_cars is 
                self._ARRAY_OF_CARS
                
        To get an object with all of the objects in the array included:
        
            e.g. car = Car.objects().get(objectId="carId", include="arrayOfDrivers")
            car.arrayOfDrivers = [ driver1, driver2, ...]
            
        If the include is not provided, then the array will contain
        unformatted JSON objects.
            
        Also the array may contain different types of objects.
        
        -------------------------------

    ### Dates:
        
        Dates are attributes whose name starts with date_.
        These attributes can be set to datetime.datetime 
        or datetime.date
        Need to use timezone when using datetime.
        Note that dates are always stored in utz isoformat!
        Datetime objects must be aware!
        ALL DATE OBJECTS IN THIS CLASS ARE/MUST BE IN UTC FORMAT!
        
        e.g. 
            from datetime import datetime
            self.set("date_born", datetime.now(tz=X))
            self.set("date_born", date.today())

        Getting these attributes using the get method will return a 
        datetime.datetime object.
 
        createdAt and updatedAt are built-in date types.

        -------------------------------

    ### Files:

        Image attributes contain the word image or avatar.
        Use get with a postfix of _url to get the url.

        e.g. 
            self.employee_image
            self.get('employee_image_url')
            
    ### GeoPoints:
    
        Attribute whose name is coordinates is considered a geo point.
        I will change this (maybe) in the future if I plan to release
        the source code. 
        coordinates are cached as a list [latitude, longitude]

    Instance Methods
    -----------------------------------------------------------
    ### self.get(attr)
        
        All class attributes values should be obtained using this
        method. However, objectId, createdAt, updatedAt may
        be accessed without having to use this method.

        createdAt and updatedAt are of __type Date.
        
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

    Class methods
    ---------------------------------------------------------

    ### ParseObject.objects()
        
        All ParseObjects come with an objects manager.
        This manager handles queries, and other things.

        e.g. To get the number of Persons whose name is jason:

            class Person(ParseObject): pass
            Person.objects().count(name="jason")


    """
    
    # Parse object built-ins - these cannot be used in the get method
    BUILTINS = ("objectId", "createdAt", "updatedAt", "ACL")

    @classmethod
    def objects(cls):  
        if not hasattr(cls, "_manager"):
            setattr(cls, "_manager", ParseObjectManager(cls))
        return cls._manager
        
    @classmethod  
    def fields_required(cls):
        """
        Return a tuple of instance variables that cannot be null.
        The first item in this tuple must be the __class__.
        
        Fields that are required together are in a tuple. These fields
        are either all null or all not null.
        If a dict is inside a tuple then all fields in the tuple must
        not be null and the dict must be True. Keys of the dict may
        have double underscores delimiting Parse query options
        like ne (not equal).
        
        Fields that are in a list must have at least 1 member that is
        not null. Only strings are allowed.
        
        No nesting is allowed (no lists/tuples within lists/tuples)
        or dicts within dicts. However, dicts may be within
        tuples (no dicts within lists).
        """
        raise NotImplementedError("Must implement this for " +\
            "validate_models management command.")

    def __init__(self, create=True, **data):
        """
        Inserts data into to self.__dict__.
        This must be called at the end of the __init__ method of the
        subclass if provided.
        
        All data are inserted if the create parameter is not set to 
        False (default is True).
        e.g. 
            class Person(ParseObject): pass
            person = Person(create=True, name="nick", age=9)

        Otherwise, only the data that is in __dict__ is inserted.
        e.g. 
            class Person(ParseObject): pass
            person = Person(create=False, name="nick", age=9)
        In the above example name is inserted but not age.

        All ParseObjects have 3 attributes by default:
            objectId, createdAt, updatedAt
        All ParseObjects also, optionally, has another attribute:
            ACL
        """
        #for builtin in ParseObject.BUILTINS:
        #    setattr(self, builtin, data.get(builtin))
        
        # these assignments are actually pointless since it gets
        # formatted in update_locally anyways
        self.objectId = data.get("objectId")
        self.ACL = data.get("ACL")
        # note that createdAt and updatedAt always comes as an iso
        # string, whereas parse Date objects' iso string are inside
        # a dict!
        self.createdAt = data.get("createdAt")
        self.updatedAt = data.get("updatedAt")
        self.update_locally(data, create)

    def path(self):
        """ returns the path of this class or use with parse 
        returns classes/ClassName
        """
        if self.__class__.__name__ == USER_CLASS:
            return 'classes/' + "_User"
        else:
            return "classes/" + self.__class__.__name__

    def update_locally(self, data, create=True):
        """
        Replaces values of matching attributes in data
        capitalized attributes only store an objectId.
        If the attribute does not exist, it is created.
        Pointer caches are created if data for the Pointer is in data.
        """
        for key, value in data.iteritems():

            # don't touch relation attrs, pointer meta, and array pointer meta 
            if (key.endswith("_") and key[0].isupper()) or\
                (key.islower() and key.startswith("_")) or\
                (key.isupper() and key.startswith("_")) or\
                (key not in self.__dict__ and not create):
                continue
                
            # handle ACL right away
            if key == "ACL":
                setattr(self, key, value)
                continue

            # Pointers attrs- store the objectId and create cache
            # attr if whole data is included
            if key[0].isupper() and type(value) is dict:
                setattr(self, key, value.get('objectId'))
                if not str(value.get("__type")) == "Pointer":
                    # if pointer meta exist then use it
                    if "_" + key.lower() in self.__dict__:
                        className = self.__dict__["_" + attr.lower()]
                    else:
                        className = key
                    setattr(self, key[0].lower() + key[1:], 
                        get_class(className)(**value))
                        
            # image file type
            elif is_image(key) and type(value) is dict: 
                setattr(self, key, value.get('name'))
                setattr(self, key + "_url", value.get('url').replace(\
                    "http:/", "https://s3.amazonaws.com")) 
                    
            elif is_image(key) and key.endswith("_url") and\
                type(value) is not dict and value:
                setattr(self, key, value.replace(\
                    "http:/", "https://s3.amazonaws.com")) 
                
            # make sure dates are datetime objects
            elif key.startswith("date_") and type(value) is dict:
                setattr(self, key, 
                            parser.parse(value.get('iso')) )
            elif key.startswith("date_") and\
                type(value) in (str, unicode):
                setattr(self, key, 
                            parser.parse(value) )
            elif key in ("createdAt", "updatedAt") and\
                type(value) in (str, unicode):
                setattr(self, key, parser.parse(value) )
                
            # GeoPoint
            elif key == "coordinates" and type(value) is dict:
                setattr(self, key, 
                    [value.get('latitude'),value.get('longitude')] )
                    
            # check if it is an array of pointers
            # as with dates and pointers, skip if the array already 
            # contains formatted data (ParseObjects)
            elif "_" + key.upper() in self.__dict__ and value and\
                len(value) > 0 and type(value[0]) is dict:
                obj_array = []
                for v in value:
                    obj_array.append(get_class(v['className'])(**v))
                        
                setattr(self, key, obj_array)
            
            else:
                setattr(self, key, value)
                
    def jsonify(self):
        """
        Returns a json (dict) object representation of this object.
        This is crutial for portability to ajax since datetime
        objects is not JSON serializable.
        
        Cache attributes are not returned!
        """
        data = {}
        for key, val in self.__dict__.copy().iteritems():
            if key.startswith("date_") or\
                key in ("createdAt", "updatedAt"):
                if val is not None:
                    data[key] = val.isoformat()
            # must be strings/unicode, numbers (int, long, float),
            # dicts, or lists/tuples!
            elif type(val) in JSONIFIABLE_TYPES:
                if "_" + key.upper() in self.__dict__ and\
                    len(val) > 0:
                    data[key] = []
                    for obj in val:
                        # need to include className
                        jsonified = obj.jsonify()
                        jsonified['className'] = obj.__class__.__name__
                        data[key].append(jsonified)
                        
                else:
                    data[key] = val
            
        return data

    def fetch_all(self, clear_first=False, with_cache=True):
        """
        Gets all of this object's data from parse and update all
        of its value locally. This includes pulling each pointer for
        caching.
        
        If clear_first, sets all non-BUILTINS in __dict__ to None.
            - note that cache attrs are also set to None
        If with_cache, retrieves all the cache attributes.
        """
        if clear_first:
            keys = self.__dict__.keys()
            for key in keys:
                if key not in ParseObject.BUILTINS:
                    self.__dict__[key] = None
                    
        if with_cache:
            cache_attrs = ""
            # fill up the Pointer cache attributes and array of pointers
            for key in self.__dict__.iterkeys():
                if key[0].isupper() and not key.endswith("_") and\
                    not key == "ACL":
                    cache_attrs = cache_attrs + key + ","
            
            if len(cache_attrs) > 0:
                res = parse("GET", self.path() + "/" + self.objectId,
                    query={ "include": cache_attrs })
            else:
                res = parse("GET", self.path() + "/" + self.objectId)
        
        else:
            res = parse("GET", self.path() + "/" + self.objectId)
            
        if res and "error" not in res:
            self.update_locally(res, False)
            return True
            
        return False

    def increment(self, attr, amount):
        """
        increments this object's attribute by amount.
        Attribute must be an integer!
        """
        res = parse("PUT", self.path() + "/" + self.objectId, {
                attr: {
                 "__op": "Increment",
                 "amount": amount } })
        if res and "error" not in res:
            self.set(attr, self.__dict__.get(attr) + amount)
            return True
        return False

    def get(self, attr, **constraints):
        """ 
        returns attr if it is not None, otherwise fetches the 
        attr from the Parse DB and returns that. 

        If the attr is a #2, then it is treated
        as a cache for a ParseObject. Note that all of this 
        attribute's data is retrieved.
        
        Getting an array of pointers using this method will return
        a list of ParseObjects with only the objectId set even if
        an include is provided.

        Constraints may also be provided to filter objects
        in a relation. If limit of 0 is given or result is empty, 
        then the cache will be set to None. If count is given,
        then this method will return the count and not the list.
        """
        # all objects have these by default. These should not be  
        # manually set to None!
        if attr in ParseObject.BUILTINS:
            return self.__dict__.get(attr)
            
        if self.__dict__.get(attr) is not None:
            # make sure that if count constraints are
            # present the cache does not block 
            if not (attr[0].islower() and attr[0].upper() +\
                attr[1:] + "_" in self.__dict__ and\
                'count' in constraints):
                return self.__dict__.get(attr)
                
        # Pointer cache 
        if attr[0].islower() and\
            self.__dict__.get(attr[0].upper() + attr[1:]):
            # if pointer meta exist then use it
            if "_" + attr.lower() in self.__dict__:
                className = self.__dict__["_" + attr.lower()]
            else:
                className = attr[0].upper() + attr[1:]
            q = {}
            if "include" in constraints:
                q["include"] = constraints['include']
            res = parse("GET", "classes/" + className +\
                    "/" + self.__dict__.get(attr[0].upper() +\
                    attr[1:]), query=q)
            if res and "error" not in res:
                setattr(self, attr, get_class(className)(**res))
            else:
                return None

        # Relation cache
        elif attr[0].islower() and attr[0].upper() + attr[1:] +\
                "_" in self.__dict__:
            className = self.__dict__[attr[0].upper() + attr[1:] + "_"]
            # need to use _user as classname if it is the USER_CLASS
            if className == USER_CLASS:
                tmp = "_User"
            else:
                tmp = className
            relName = attr[0].upper() + attr[1:]
            where_dict = {
                        "$relatedTo":{ 
                        "object":{
                            "__type": "Pointer",
                            "className": self.path().split('/')[1],
                            "objectId": self.objectId},
                        "key": relName},  }
            where_dict.update(query(constraints, where_only=True))
            q = {}
            q.update({"where":dumps(where_dict)})
            # add the not where options
            for k,v in constraints.iteritems():
                if k in NOT_WHERE_CONSTRAINTS:
                    q.update({k:v})
            res = parse("GET", 'classes/' + tmp, query=q)
            if res and "error" not in res:
                if len(res['results']) == 0:
                    setattr(self, attr, None)
                else:
                    c = get_class(className)
                    setattr(self, attr, 
                                [ c(**d) for d in res['results'] ])
                if 'count' in res:
                    return res['count']
            else:
                if 'count' in constraints:
                    return 0
                return None 
                
        # date object
        elif attr.startswith("date_"):
            res = parse("GET", self.path(), query={"keys":attr,
                    "where":dumps({"objectId":self.objectId})})
            if 'results' in res and res['results']:
                setattr(self, attr, 
                    parser.parse(res.get('results')[0].get(\
                        attr).get("iso")))
                        
        # Image types 
        elif is_image(attr) and attr.endswith("_url") and\
            attr.replace("_url", "") in self.__dict__:
            attr_name = attr.replace("_url","")
            
            res = parse("GET", self.path(), query={"keys":attr_name,
                    "where":dumps({"objectId":self.objectId})})
                    
            if 'results' in res and res['results']:
                img = res['results'][0].get(attr_name)
                if img:
                    setattr(self, attr, img.get('url').replace(\
                        "http:/", "https://s3.amazonaws.com")) 
                    setattr(self, attr_name, img.get('name'))
                    
        # attr is a geopoint
        elif attr == "coordinates" and attr in self.__dict__:
            res = parse("GET", self.path(), query={"keys":attr,
                    "where":dumps({"objectId":self.objectId})})
            if 'results' in res and res['results']:
                coordinates = res['results'][0].get("coordinates")
                latitude = coordinates.get("latitude")
                longitude = coordinates.get("longitude")
                if coordinates and latitude and longitude:
                    setattr(self, attr, [latitude, longitude])
                else:
                    setattr(self, attr, None)
                    
        # array of pointers
        elif "_" + attr.upper() in self.__dict__:
            q={"keys":attr,
                    "where":dumps({"objectId":self.objectId})}
            if "include" in constraints:
                q["include"] = constraints['include']     
                
            res = parse("GET", self.path(), query=q)
            if 'results' in res and res['results']:
                result = res['results'][0][attr]
                if result is not None:
                    setattr(self, attr, [ get_class(\
                        v['className'])(**v) for v in result ])
            
        # attr is a regular attr or Pointer/Relation attr
        elif attr in self.__dict__: 
            res = parse("GET", self.path(), query={"keys":attr,
                    "where":dumps({"objectId":self.objectId})})
            if 'results' in res and res['results']:
                # what if Pointer attr was set to None?
                # getting them will return a dict!
                if attr[0].isupper() and not attr.endswith("_"):
                    p = res.get('results')[0].get(attr)
                    if type(p) is dict:
                        setattr(self, attr, p.get("objectId") )
                    else:
                        setattr(self, attr, None)
                else:
                    setattr(self, attr, res.get('results')[0].get(attr) )
                
        return self.__dict__.get(attr)

    def set(self, attr, val):
        """ set this object's attr to val. This does not commit
        anything up to Parse. """
        setattr(self, attr, val)
        return True

    # NOTE array operations do not affect the array cache!
    def array_add_unique(self, arrName, vals):
        """ adds the list of vals to the array with the given name
        If the array in Parse is currently null, this sets the 
        array to vals. This does not check for uniqueness in vals.
        """
        return self._array_op('AddUnique', arrName, vals)

    def array_remove(self, arrName, vals):
        """ removes the list of vals from the array.
        If the array in Parse is currently null, this sets the 
        array to vals. This does not check for uniqueness in vals.
        """
        return self._array_op('Remove', arrName, vals)

    def _array_op(self, op, arrName, vals):
        """ array operations 
        If the array corresponding to arrName is an array of pointers,
        vals must be an array of ParseObjects. WARNING! This will
        set the current array to the 1 returned, which only has objectId.
        """
        # format vals to pointers if it is an array of objects
        arr_ptrs = "_" + arrName.upper() 
        
        array_not_none = getattr(self, arrName) is not None
        
        if self.__dict__[arrName] is None:
            self.__dict__[arrName] = []
        
        if arr_ptrs in self.__dict__:
            vals = [ format_pointer(val.__class__.__name__, val.objectId) for\
                val in vals ]
           
        if array_not_none: # array is not null/None
            res = parse("PUT", self.path() + '/' + self.objectId, 
                {arrName: {'__op':op, 'objects':vals} })
                
        else: # array does not exist. initialize it here.
            res = parse("PUT", self.path() + '/' + self.objectId, 
                {arrName:vals })
                
        if res and 'error' not in res:
            self.update_locally(res, False)
            return True
            
        return False 
        
    def _relation_op(self, op, relAttrName, objectIds):
        """
        Helper function for add and remove relations.
        """
        if relAttrName not in self.__dict__:
            return False
        className = getattr(self, relAttrName)
        if className == USER_CLASS:
            className = "_User"
        objs = []
        for oid in objectIds:
            objs.append( { "__type": "Pointer",
                           "className": className,
                           "objectId": oid } )
        res = parse("PUT", self.path() + "/" + self.objectId, {
                    relAttrName[:-1]: {
                        "__op": op,
                        "objects": objs, 
                    }
                 } )
        if res and 'error' not in res:
            cacheAttrName = relAttrName[0].lower() + relAttrName[1:-1]
            self.__dict__[cacheAttrName] = None
            return True
        else:
            return False

    def add_relation(self, relAttrName, objectIds):
        """ Adds the list of objectIds to the given relation. 
        relAttrName is a str, which is the name of the Relation attr.

        Adds the relations to Parse and empty  the cache. 
        Returns True if successful.
        """
        return self._relation_op("AddRelation",relAttrName,objectIds)

    def remove_relation(self, relAttrName, objectIds):
        """ Adds the list of objectIds to the given relation. 
        relAttrName is a str, which is the name of the Relation attr.

        Adds the relations to Parse and empty  the cache. 
        Returns True if successful.
        """
        return self._relation_op("RemoveRelation",
            relAttrName,objectIds)
        

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
            self.update_locally(res, False)
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
        res = parse('POST', self.path(), data)
        if res and "error" not in res:
            self.update_locally(res, False)
            return True
        
        return False

    def delete(self):
        """ delete the row corresponding to this object in Parse """
        res = parse("DELETE", self.path() + '/' + self.objectId)
        if 'error' not in res:
            return True
        return False

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
                setattr(self, key, None)
                continue
            # exclude the Pointer cache and maybe clear it
            if  key[0].islower() and\
                (key[0].upper() + key[1:] in self.__dict__):
                # clear the cache objects if their pointers changed
                if value and value.objectId !=\
                    self.__dict__[key[0].upper() + key[1:]]:
                    setattr(self, key, None)
                continue
            # exclude image url
            if is_image(key) and key.endswith("_url"):
                # NOTE cache is not cleared so manually set cache
                # to None when changing file!
                continue

            # exclude Pointer meta and array of pointers meta
            if (key.islower() and key.startswith("_")) or\
                (key.isupper() and key.startswith("_")):
                continue

            # Pointers
            if key[0].isupper() and not key.endswith("_") and\
                key != "ACL":
                # use pointer meta value as classname if exist
                if "_" + key.lower() in self.__dict__:
                    data[key] =\
                      format_pointer(self.__dict__["_" + key.lower()],
                        value)
                else:
                    data[key] = format_pointer(key, value)
            # Dates
            elif key.startswith("date_") or\
                key in ("createdAt", "updatedAt"):
                data[key] = format_date(value)
            # Image files
            elif is_image(key):
                data[key] = format_file(value)
            # GeoPoint
            elif key == "coordinates" and value:
                data[key] = format_geopoint(value[0], value[1])
            elif key == "ACL":
                # note that ACL must be a hash/dict!!!
                if value is not None and type(value) is dict:
                    data[key] = value
                    
            # array of pointers not None or empty list
            elif "_" + key.upper() in self.__dict__ and value:
                data[key] = [ format_pointer(val.__class__.__name__, val.objectId) for\
                    val in value ]
                    
            # regular attributes
            else:
                data[key] = value
                
        return data

