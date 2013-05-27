"""
Core models for the Parse interface.
"""
from parse.utils import parse

class ParseObject(object):
    """ Provides a Parse version of the Django models """
    def create(self):
        """ posts up the data to Parse """
        parse('POST', 'classes/' + self.__class__.__name__,
                self.__dict__)
        return True

    def delete(self):
        """ delete the row corresponding to this object in Parse """
        # TODO 
        pass

