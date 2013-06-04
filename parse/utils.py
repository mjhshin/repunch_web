"""
Helpers methods for parse.apps to enfore the DRY principle.
"""

import json, httplib, urllib

from repunch.settings import PARSE_VERSION,\
REST_CONNECTION_META_JSON, REST_CONNECTION_META_PNG

def parse(method, path, data=None, query=None,
            cMeta='json'):
    """
    sends a request to parse using specified method, url, data,
    and optionally a query.
    
    data is a dictionary/json, usually it is a ParseObject.__dict__
    query is a dictionary/json containing constraints for filtering.
    Note that is the method is GET, data parameter is ignored.

    Returns None if request does not return a json object.
    """
    conn = httplib.HTTPSConnection('api.parse.com', 443)
    conn.connect()

    if cMeta == 'json':
        rcm = REST_CONNECTION_META_JSON
    elif cMeta == 'png':
        rcm = REST_CONNECTION_META_PNG

    if method in ("POST", "PUT", "DELETE"):
        if data:
            # create a new Parse object
            if cMeta == 'json':
                conn.request(method, '/' + PARSE_VERSION + '/' +\
                        path, json.dumps(data), rcm)
            elif cMeta == 'png':
                # delete a file
                if method == "DELETE":
                    conn.request(method, '/' + PARSE_VERSION + '/' +\
                        path, '', rcm)
                # create a file
                elif method == "POST":
                    with open(data, 'r') as fid:
                        conn.request(method, '/' + PARSE_VERSION +\
                            '/' + path, fid, rcm)
                        fid.close()
        else:
            conn.request(method, '/' + PARSE_VERSION + '/' +\
                        path, '', rcm)

    elif method == "GET":
        if query:
            params = '?' + urllib.urlencode(query)
        else:
            params = ''
        conn.request("GET", '/' + PARSE_VERSION + '/' + path +\
                '%s' % (params, ), '',  rcm)

    try:
        result = json.loads(conn.getresponse().read())
    except ValueError as e:
        conn.close()
        return None

    conn.close()

    return result

    
def create_file(filePath, fName, fType):
    """ 
    creates the given filePath with the given name and type 
    """
    return parse("POST", 'files/' + fName, filePath, cMeta=fType)
    

def delete_file(name, fType):
    """ deletes the given file """    
    res = parse("DELETE", 'files/' + name, cMeta=fType)
    print name
    print name
    print name
    print name
    if res and 'error' not in res:
        return True
    return False








