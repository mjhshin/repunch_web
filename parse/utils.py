"""
Helpers methods for parse.apps to enfore the DRY principle.
"""
from django.utils import timezone
from dateutil.tz import tzutc
from dateutil import parser
import json, httplib, urllib, re
from PIL import Image

from repunch.settings import PARSE_VERSION,\
REST_CONNECTION_META, SUPPORTED_IMAGE_FORMATS,\
PARSE_MASTER_KEY, PARSE_IMAGE_DIMENSIONS as PID

BAD_FILE_CHR = re.compile('[\W_]+')

import traceback

def parse(method, path, data=None, query=None,
            cMeta='json', timeout=None):
    """
    sends a request to parse using specified method, url, data,
    and optionally a query.
    
    data is a dictionary/json, usually it is a ParseObject.__dict__
    query is a dictionary/json containing constraints for filtering.
    Note that is the method is GET, data parameter is ignored.

    Returns None if request does not return a json object.
    """
    if timeout:
        conn = httplib.HTTPSConnection('api.parse.com',
                                        443, timeout=timeout)
    else:
        conn = httplib.HTTPSConnection('api.parse.com', 443)
    conn.connect()

    rcm = REST_CONNECTION_META.copy()
    rcm["Content-Type"] = "application/" + cMeta

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
        if method == "POST" and cMeta in SUPPORTED_IMAGE_FORMATS:
            conn.close()
        return None
    conn.close()
    return result

def rescale(image_path, img_format, crop_coords=None,
        dst_width=PID[0], dst_height=PID[1]):
    img = Image.open(image_path)
    
    src_width, src_height = img.size
    src_ratio = float(src_width) / float(src_height)
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
        
    # crop if given the coords
    if crop_coords:
        x1 = crop_coords["x1"]
        y1 = crop_coords["y1"]
        x2 = crop_coords["x2"]
        y2 = crop_coords["y2"]
        img = img.crop((x1, y1, x2, y2))
    img = img.resize((int(dst_width), int(dst_height)), Image.ANTIALIAS)
        
    img.save(image_path, img_format)

def create_png(file_path, coords=None):
    """ 
    creates the given uploadedFile, which is a png image.
    """
    im = Image.open(file_path)
    im.save(file_path, 'png')
    rescale(file_path, 'png', coords)
    file_name = file_path.split("/")[-1]
    res = parse("POST", 'files/' + BAD_FILE_CHR.sub('',
                file_name), file_path, cMeta='png')
    return res 

def delete_file(name, fType):
    """ deletes the given file """   
    return parse("DELETE", 'files/' + name, cMeta=fType)

def cloud_call(func_name, params, timeout=None):
    """ Calls a cloud function with the name func_name and with
    the parameters params. """
    return parse("POST", "functions/" + func_name,
            params, timeout=timeout)
            
            
def make_aware_to_utc(dtime, tzone):
    """
    Takes in an unaware datetime object, makes it aware using the 
    timezone in the session and returns a datetime object in utc.
    """
    # make aware
    dtime = timezone.make_aware(dtime, tzone)
    # then convert to utc format
    return timezone.localtime(dtime, tzutc())
    
def title(string):
    """
    Like str.title but does not capitalize letter after '
    """
    return " ".join([word.capitalize() for word in string.split(" ")])
    
    





