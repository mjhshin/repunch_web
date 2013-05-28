"""
Core models for the Parse interface.
"""

from parse.utils import parse

class ParseObject(object):
    """ Provides a Parse version of the Django models 
        This class is abstract and no concrete objects should be
        created using this class.
    """
    def __init__(self):
        self.objectId = None
        self.createdAt = None
        self.updatedAt = None
        pass

    def path(self):
        """ returns the path of this class or use with parse 
            returns classes/ClassName
        """
        return "classes/" + self.__class__.__name__
        
connection.request('PUT', '/1/classes/GameScore/7Lw8Jo8Lv0', json.dumps({
       "opponents": {
         "__op": "AddRelation",
         "objects": [
           {
             "__type": "Pointer",
             "className": "Player",
             "objectId": "x64dPWz09W"
           }
         ]
       }
     }),  REST_CONNECTION_META)


    def update(self):
        """ Save changes to this object to the Parse DB.
            Returns True if update is successful. 
            
            If there exist a relation to other objects,
            this method makes sure that the relation exists.
        """
        rels = []
        # check for relations
        for f in self.__dic__.iterkeys():
            if f.endswith("_id"):
                rels.append(f)

        # format the relation to put in data
        if rels:
            data = self.__dict__[:]
            for rel in rels:
                pass
            parse("PUT", self.path(), data, self.objectId)
        else:
            parse("PUT", self.path(), self.__dict__, self.objectId)

    def fetchAll(self):
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

        Must override this if there is any type of relation that this 
        object has with other objects.
        """
        res = parse('POST', path, self.path())
        self.createdAt = res["createdAt"]
        self.objectId = res["objectId"]
        return True

    def delete(self):
        """ delete the row corresponding to this object in Parse """
        # TODO 
        pass

