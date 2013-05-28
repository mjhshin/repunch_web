"""
Core models for the Parse interface.
"""
from parse.utils import parse

class ParseObject(object):
    """ Provides a Parse version of the Django models """
    def __init__(self):
        # for future additions
        pass

    def update(self):
        """ Saves changes to this object to the Parse DB.
            Returns True if update is successful. """
        # TODO
        pass

    def save(self):
        """ 
        saves/creates this object to the DB. This does not check 
        uniqueness of any field. 
        Use update to save an existing object.

        Note that self.__dict__ contains objectId which will result
        to the parse request returning an error only if it is not None
        """
        path = 'classes/' + self.__class__.__name__
        parse('POST', path, self.__dict__)
        return True

    def delete(self):
        """ delete the row corresponding to this object in Parse """
        # TODO 
        pass

