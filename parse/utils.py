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
        cMeta = REST_CONNECTION_META_JSON
    elif cMeta == 'png':
        cMeta = REST_CONNECTION_META_PNG

    if method in ("POST", "PUT", "DELETE"):
        if data:
            d = json.dumps(data)
        else:
            d = ''
        conn.request(method, '/' + PARSE_VERSION + '/' + path, 
                        d, cMeta)
    elif method == "GET":
        if query:
            params = '?' + urllib.urlencode(query)
        else:
            params = ''
        conn.request("GET", '/' + PARSE_VERSION + '/' + path +\
                '%s' % (params, ), '',  cMeta)

    try:
        result = json.loads(conn.getresponse().read())
    except ValueError as e:
        conn.close()
        return None

    conn.close()

    return result

    
    















