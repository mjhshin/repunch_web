"""
Parse models corresponding to Django models
"""

from parse.utils import parse

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
            A Relation is a constant string, which is the name.

        2. If the first letter of an lower case and there exist a #1
            matching the attr if it was capitalized, 
            then the attr will not be saved to Parse.
            This can be used as a cache.
            A cache for a Pointer contains None or a ParseObject.
            A cache for a Relation contains None or a list of
            ParseObjects.
           
        2.5 Also, the value of a Relation attr is not pushed up.
            Use add_relations for Relations.

        3. the init method of this class must be called in the 
            __init__ method of the subclass with the initial data

        4. use the get(self, attr) method to get an attribute.
            Do not reference the attrs directly by using a dot UNLESS
            the attribute is objectId, createdAt, or updatedAt.
    """
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
                if "error" not in res:
                    c = self.get_class(className)
                    self.__dict__[attr] = c(res)
                else:
                    return None

        # Relation cache
        elif attr[0].islower() and attr[0].upper() + attr[1:] +\
                "_" in self.__dict__:
            # TODO

        else: # attr is a regular attr
            res = parse("GET", self.path(), query={"keys":attr})
            self.update_locally(res.get('results')[0])

        return self.__dict__[attr]

    def set(self, attr, val):
        """ set this object's attr to val. This does not commit
        anything up to Parse. """
        self.__dict__[attr] = val

    def add_relation(self, rel, objectIds):
        """ Adds the list of objectIds to the given relation rel 
        Adds the relations to Parse and empty 
        the cache. Returns True if successful.
        """
        if rel not self.__dict__:
            return False
    
        # TODO

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

        res = parse("PUT", self.path(), data, self.objectId)
        if res:
            if "error" in res:
                return False
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
        
        if res:
            if "error" in res:
                return False
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
            if key.endswith("_") or (key[0].islower() and\
                key[0].upper() + key[1:] + "_" in self.__dict__):
                continue
            if  key[0].islower() and\
                (key[0].upper() + key[1:] in self.__dict__):
                # clear the cache objects if their pointers changed
                if value and value.objectId !=\
                    self.__dict__[key[0].upper() + key[1:]]:
                    self.__dict__[key[0].upper() + key[1:]] = None
                continue
            data[key] = value
        return data

