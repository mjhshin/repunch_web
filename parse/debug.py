"""
Some methods to make debugging easier.
"""

def print_dict(dic):
    """ just prints out the key : value of dic in a pretty way """
    print "Key\t\t\tValue"
    for key, value in dic.iteritems():
        print "%s\t\t\t%s" % (key, value) 
