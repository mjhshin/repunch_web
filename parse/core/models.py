"""
Parse models corresponding to Django models
"""
from json import dumps
from dateutil import parser

from repunch.settings import USER_CLASS
from parse.utils import parse
from parse.core.formatter import query,\
format_date, format_pointer

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
        if res:
            return res[0]

    def filter(self, **constraints):
        """ 
        Returns the list of objects that matches the constraints.
        
        See WHERE_OPTIONS for all currently supported options.
        Double underscores allow for usage of WHERE_OPTIONS like 
        gte (greater than or equal to). 

        TODO Also allows queries spanning multiple classes.
        """
        res = parse("GET", self.path, query=query(constraints))
                  
        if res and "results" in res:
            objs = []
            for data in res['results']:
                objs.append(self.cls(**data))     
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

        These attributes need to store a dictionary containing at 
        least the objectId. 
        The name of the attribute is used as the column name in Parse.

        A cache attribute is created that contains the actual 
        ParseObject (initially None) that it points to.
        The cache attribute name is the Pointer name with the first
        character lowercased. To get the actual object:
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
        These attributes can be set to datetime.datetime 
        or datetime.date
        
        e.g. 
            from datetime import datetime
            self.set("date_born", datetime.now())
            self.set("date_born", date.today())

        Getting these attributes using the get method will return a 
        datetime.datetime object.

        -------------------------------

    Instance Methods
    -----------------------------------------------------------
    ### self.get(attr)
        
        All class attributes values should be obtained using this
        method. However, objectId, createdAt, updatedAt may
        be accessed without having to use this method.

        createdAt and updatedAt are of __type Date.
        However, they are always stored as strings in iso format in
        ParseObjects.
        
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

            class Person(ParseObject):
                pass
            Person.objects().count(name="jason")


    """

    @classmethod
    def objects(cls):  
        if not hasattr(cls, "_manager"):
            setattr(cls, "_manager", ParseObjectManager(cls))
        return cls._manager

    def __init__(self, create=True, **data):
        """
        Inserts data into to self.__dict__.
        This must be called at the end of the __init__ method of the
        subclass if provided.
        
        All data are inserted if the create parameter is not set to 
        False (default is True).
        e.g. 
            class Person(ParseObject):
                pass
            person = Person(create=True, name="nick", age=9)

        Otherwise, only the data that is in __dict__ is inserted.
        e.g. 
            class Person(ParseObject):
                pass
            person = Person(create=False, name="nick", age=9)
        In the above example name is inserted but not age.

        All ParseObjects have 3 attributes by default:
        objectId, createdAt, updatedAt
        """
        self.objectId = data.get("objectId")
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
            if key.endswith("_") or (key not in self.__dict__ and\
                not create):
                continue

            # Pointers attrs- store only the objectId
            if key[0].isupper() and type(value) is dict:
                setattr(self, key, value.get('objectId'))
            # make sure dates are datetime objects
            elif key.startswith("date_") and type(value) is dict:
                setattr(self, key, 
                            parser.parse(value.get('iso')) )
            else:
                setattr(self, key, value)

    def get_class(self, className):
        """
        Need to override this for every class in order to use caching.
        Returns the class with the className.
        TODO Automate this process?
        """
        return None

    def fetchAll(self):
        """
        Gets all of this object's data from parse and update all
        of its value locally.
        """
        res = parse("GET", self.path() + "/" + self.objectId)
        if res and "error" not in res:
            self.update_locally(res, False)

    def get(self, attr):
        """ returns attr if it is not None, otherwise fetches the 
        attr from the Parse DB and returns that. 

        If the attr is a #2, then it is treated
        as a cache for a ParseObject. Note that all of this 
        attribute's data is retrieved.
        """
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
                setattr(self, attr, c(**res))
            else:
                return None

        # Relation cache
        elif attr[0].islower() and attr[0].upper() + attr[1:] +\
                "_" in self.__dict__:
            className = self.__dic__[attr[0].upper() + attr[1:] + "_"]
            # need to use _user as classname if it is the USER_CLASS
            if className == USER_CLASS:
                tmp = "_User"
            else:
                tmp = className
            relName = attr[0].upper() + attr[1:]
            res = parse("GET", 'classes/' + tmp, query={
                    "where":dumps({
                        "$relatedTo":{ 
                        "object":{
                            "__type": "Pointer",
                            "className": self.path().split('/')[1],
                            "objectId": self.objectId},
                        "key": relName, }  })  })
            if res and "error" not in res:
                c = self.get_class(className)
                setattr(self, attr, 
                            [ c(**d) for d in res['results'] ])
            else:
                return None 
        # date object
        elif attr.startswith("date_"):
            res = parse("GET", self.path(), query={"keys":attr,
                    "where":dumps({"objectId":self.objectId})})
            if 'results' in res and res['results']:
                setattr(self, attr, 
                    parser.parse(res.get('results')[0].get(attr)) )
        # attr is a regular attr or Pointer/Relation attr
        elif attr in self.__dict__: 
            res = parse("GET", self.path(), query={"keys":attr,
                    "where":dumps({"objectId":self.objectId})})
            if 'results' in res and res['results']:
                setattr(self, attr, res.get('results')[0].get(attr) )

        return self.__dict__.get(attr)

    def set(self, attr, val):
        """ set this object's attr to val. This does not commit
        anything up to Parse. """
        # TODO check attr and val validity
        setattr(self, attr, val)
        return True

    def add_relation(self, relAttrName, objectIds):
        """ Adds the list of objectIds to the given relation. 
        relAttrName is a str, which is the name of the Relation attr.

        Adds the relations to Parse and empty  the cache. 
        Returns True if successful.
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
            self.update_locally(res, True)
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
            self.update_locally(res, True)
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

            # Pointers
            if key[0].isupper() and not key.endswith("_"):
                data[key] = format_pointer(key, value)
            # Dates
            elif key.startswith("date_"):
                data[key] = format_date(value)
            # regular attributes
            else:
                data[key] = value
        return data

