"""
Helpers methods for parse.apps to enfore the DRY principle.
"""

import json, httplib, urllib, tempfile, re, string
from PIL import Image

from repunch.settings import PARSE_VERSION,\
REST_CONNECTION_META_JSON, REST_CONNECTION_META_PNG

BAD_FILE_CHR = re.compile('[\W_]+')

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
        rcm = REST_CONNECTION_META_JSON.copy()
    elif cMeta == 'png':
        rcm = REST_CONNECTION_META_PNG.copy()

    d = None

    if method in ("POST", "PUT", "DELETE"):
        if data:
            # create a new Parse object
            if cMeta == 'json':
                conn.request(method, '/' + PARSE_VERSION + '/' +\
                        path, json.dumps(data), rcm)
            elif cMeta == 'png':
                # delete a file
                if method == "DELETE":
                    rcm["X-Parse-Master-Key"] =\
                         "CW0aN2fsmS4vap0Q4LJ1OxH9zYAN4Ev9clzopjSy"
                    conn.request(method, '/' + PARSE_VERSION + '/' +\
                        path, '', rcm)
                # create a file
                elif method == "POST":
                    conn.request(method, '/' + PARSE_VERSION +\
                            '/' + path, open(data, 'r'), rcm)
                    # data.close() don't close the file yet!
                    # transaction may not be done, wait for response!
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
        if method == "POST" and cMeta == "png" and d:
            conn.close()
        return None

    conn.close()
    return result

    
def create_png(uploadedFile):
    """ 
    creates the given uploadedFile, which is a png image.
    """
    im = Image.open(uploadedFile.file)
    tmp = tempfile.NamedTemporaryFile()
    # don't auto delete the tmp file on close
    tmp.delete = False
    im.save(tmp, 'png')
    tmp.close()
    # filenames with spaces and tabs causes broken pipe!
    # also filename must be alpha-numeric! 
    # Otherwise, BadFileName results
    res = parse("POST", 'files/' + BAD_FILE_CHR.sub('',
                uploadedFile.name), tmp.name, cMeta='png')
    # don't forget to delete the file
    tmp.unlink(tmp.name)
    return res

def delete_file(name, fType):
    """ deletes the given file """    
    return parse("DELETE", 'files/' + name, cMeta=fType)








