"""
Package wide methods
"""

def isdigit(string):
    # use because "-1".isdigit() is False
    try:
        int(string)
    except:
        return False
    else:
        return True
