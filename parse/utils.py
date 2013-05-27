"""
Helpers methods for parse.apps to enfore the DRY principle.
"""

import json, httplib

from repunch.settings import PARSE_VERSION, REST_CONNECTION_META

def to_parse(method, operation, data):
    """
    sends a request to parse using specified method, operation, and data
    data is a dictionary, usually the object.__dict__
    """
    conn = httplib.HTTPSConnection('api.parse.com', 443)
    conn.connect()
    conn.request(method, operation, 
                    json.dumps(data), REST_CONNECTION_META)
    result = json.loads(connection.getresponse().read())
    conn.close()
    return result
