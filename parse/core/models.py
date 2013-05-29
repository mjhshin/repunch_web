"""
Core models for the Parse interface.
"""

from parse.utils import parse

class ParseObject(object):
    """ Provides a Parse version of the Django models 
    This class is abstract and no concrete objects should be
    created using this class.

    Rules:
        1. If the first letter of an attribute is capitalized, then
            it is treated as a Pointer or Relation
        2. If the first letter of an lower case and there exist a #1
            matching the attr if it was capitalized, 
            then the attr will not be saved to Parse.
            This can be used as a cache.
    """
    def __init__(self):
        self.objectId = None
        self.createdAt = None
        self.updatedAt = None

    def path(self):
        """ returns the path of this class or use with parse 
        returns classes/ClassName
        """
        return "classes/" + self.__class__.__name__

    def update_locally(self, data):
        """
        Replaces values of matching attributes in data
        """
        for key, value in data.iteritems():
            if key in self.__dict__.iterkeys():
                self.__dict__[key] = value

    def get_relations(self):
        """
        Returns a dictionary of relations of this class.
        A relation is an attribute of this class if the first
        character of the attribute is capitalized.
        """
        rels, data = [], {}
        # check for relations 
        # rels will now contain a list of tuples (className, objectId)
        for key, value in self.__dict__.iteritems():
            if key[0].isupper():
                rels.append( (key, value) )
        # populate the data in proper format
        if rels:
            for rel in rels:
                data[rel[0]] = {
                    "__type": "Pointer",
                    "className": rel[0],
                    "objectId": rel[1]
                }
        return data

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
        if self.__dict__.get(attr) is not None and\
            not (key[0].islower() and\
                    key.capitalize() in self.__dict__):
            return self.__dict__.get(attr)

        # fetch the data
        res = parse("GET", "classes/" + attr.capitalize() +\
                        "/" + self.__dict__.get(attr.capitalize()))
        if "error" not in res:
            c = self.get_class(attr.capitalize())
            self.__dict__[attr] = c(res)
    
        return self.__dict__.get(attr)

    def update(self):
        """ Save changes to this object to the Parse DB.
        Returns True if update is successful. 
        
        If there exist a relation to other objects,
        this method makes sure that the relation exists.
        """
        # exclude cache attrs
        data = {}
        for key, value in self.__dict__.iteritems():
            if key[0].islower() and\
                    key.capitalize() in self.__dict__:
                continue
            data[key] = value
        
        rels = self.get_relations()
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

    def refresh(self):
        """ 
        Fetches all the attributes of this object from the DB.        

        Must have the objectId available or this does nothing and
        returns False.
        """
        if not self.objectId:
            return False
        # TODO 

    def save(self):
        """ 
        saves/creates this object to the DB. This does not check 
        uniqueness of any field. 
        Use update to save an existing object.

        After a successful request, this 
        object will now have the objectId available but not the rest
        of its attributes. Use

        Note that self.__dict__ contains objectId which will result
        to the parse request returning an error only if it is not None

        If there exist a relation to other objects,
        this method makes sure that the relation exists.
        """
         # exclude cache attrs
        data = {}
        for key, value in self.__dict__.iteritems():
            if key[0].islower() and\
                    key.capitalize() in self.__dict__:
                continue
            data[key] = value

        rels = self.get_relations()
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

