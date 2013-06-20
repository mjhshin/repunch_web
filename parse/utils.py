"""
Helpers methods for parse.apps to enfore the DRY principle.
"""

import time
from datetime import datetime
import json, httplib, urllib, tempfile, re
from PIL import Image

from repunch.settings import PARSE_VERSION,\
REST_CONNECTION_META,\
PARSE_MASTER_KEY, PARSE_IMAGE_DIMENSIONS as dim

BAD_FILE_CHR = re.compile('[\W_]+')

import traceback

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

    rcm = REST_CONNECTION_META.copy()
    rcm["Content-Type"] = "application/" + cMeta
    d = None

    if method in ("POST", "PUT", "DELETE"):
        if data:
            # create a new Parse object
            if cMeta == 'json':
                conn.request(method, '/' + PARSE_VERSION + '/' +\
                        path, json.dumps(data), rcm)
            elif cMeta == 'png':
                # if method == "DELETE":
                # delete should have no data
                # create a file
                conn.request(method, '/' + PARSE_VERSION +\
                        '/' + path, open(data, 'r'), rcm)
                # data.close() don't close the file yet!
                # transaction may not be done, wait for response!
        else:
            if method == "DELETE":
                rcm.pop("X-Parse-REST-API-Key")
                rcm.pop("Content-Type")
                rcm["X-Parse-Master-Key"] = PARSE_MASTER_KEY
                conn.request(method, '/' + PARSE_VERSION + '/' +\
                        path, '', rcm)
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

def rescale(image_path, img_format, width=dim[0], height=dim[1]):
    max_width = width
    max_height = height
    img = Image.open(image_path)
    
    src_width, src_height = img.size
    src_ratio = float(src_width) / float(src_height)
    dst_width, dst_height = max_width, max_height
    dst_ratio = float(dst_width) / float(dst_height)
    
    if dst_ratio < src_ratio:
        crop_height = src_height
        crop_width = crop_height * dst_ratio
        x_offset = float(src_width - crop_width) / 2
        y_offset = 0
    else:
        crop_width = src_width
        crop_height = crop_width / dst_ratio
        x_offset = 0
        y_offset = float(src_height - crop_height) / 3
        
    # we can crop
    # img = img.crop(x0, y0, x1, y1)
    img = img.resize((int(dst_width), int(dst_height)), Image.ANTIALIAS)
        
    img.save(image_path, img_format)

    
def create_png(uploadedFile):
    """ 
    creates the given uploadedFile, which is a png image.
    """
    im = Image.open(uploadedFile.file)
    tmp = tempfile.NamedTemporaryFile()
    # don't auto delete the tmp file on close
    tmp.delete = False
    im.save(tmp, 'png')
    rescale(tmp.name, 'png')
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
    parse("DELETE", 'files/' + name, cMeta=fType)

def cloud_call(func_name, params):
    """ Calls a cloud function with the name func_name and with
    the parameters params. """
    return parse("POST", "functions/" + func_name, params)

def datetime_to_utc(dtime):
    """
    Returns a utc datetime from dtime
    """
    return datetime.utcfromtimestamp(time.mktime(dtime.timetuple()))

