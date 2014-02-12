"""
Helpers methods for parse.apps to enfore the DRY principle.
"""
from django.utils import timezone
from dateutil.tz import tzutc
from dateutil import parser
from PIL import Image
from random import randint
import json, httplib, urllib, re, os

from repunch.settings import PARSE_VERSION, PARSE_BATCH_LIMIT,\
REST_CONNECTION_META, SUPPORTED_IMAGE_FORMATS,\
PARSE_MASTER_KEY

BAD_FILE_CHR = re.compile('[\W_]+')

import traceback

def flush(session):
    """
    Flush does not call save after delete- which means that
    changes are not made immediately!
    flush calls: clear -> delete -> create
    
    This fixes that.
    """
    session.clear()
    session.delete()
    session.save()
    session.create()

def parse(method, path, data=None, query=None,
        timeout=None, content_type="application/json"):
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
    rcm["Content-Type"] = content_type

    if method in ("POST", "PUT", "DELETE"):
        if data: # POST & PUT
            if content_type == 'application/json':
                # need to add the parse session token for _User class!
                # or just include the master key!
                if method == "PUT" and path.__contains__("_User"):
                    rcm["X-Parse-Master-Key"] = PARSE_MASTER_KEY
                conn.request(method, '/' + PARSE_VERSION + '/' +\
                        path, json.dumps(data), rcm)
            elif content_type == 'image/png':
                conn.request(method, '/' + PARSE_VERSION +\
                        '/' + path, open(data, 'r'), rcm)
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
        if method == "POST" and content_type.split("/")[1] in\
            SUPPORTED_IMAGE_FORMATS:
            conn.close()
        return None
    conn.close()
    return result
    
def batch(method, parse_objects):
    """
    Create (POST), update (PUT), or delete (DELETE) multiple
    parse objects in a single call to Parse.
    
    The limit is PARSE_BATCH_LIMIT (50) parse_objects per batch!
    
    Note that the master key is used here just in case one of the
    parse_objects is a User object and method is update.
    This will also mean that ACLs are ignored here.
    """
    reqs = []
    for po in parse_objects:
        if method == "POST": 
            path = '/' + PARSE_VERSION + '/' + po.path()
        else:
            path = '/' + PARSE_VERSION + '/' + po.path() + '/' +\
                po.objectId
        d = {
            "method": method,
            "path": path,
        }
        if method != "DELETE":
            d["body"] = po._get_formatted_data()
        reqs.append(d)
        
    payload = json.dumps({"requests": reqs})
    
    rcm = REST_CONNECTION_META.copy()
    rcm["X-Parse-Master-Key"] = PARSE_MASTER_KEY
    rcm["Content-Type"] = "application/json"
    conn = httplib.HTTPSConnection('api.parse.com', 443)
    conn.connect()
    conn.request("POST", '/' + PARSE_VERSION + '/'  + "batch",
        payload, rcm)
     
    return json.loads(conn.getresponse().read())
    
def account_login(username, password):
    return parse("GET", "login", query=\
                {"username":username, "password":password} )

def rescale(image_path, img_format, size=None, crop_coords=None):
    """
    size is a tuple (width, height).
    """
    img = Image.open(image_path)
        
    # crop if given the coords
    if crop_coords:
        x1 = crop_coords["x1"]
        y1 = crop_coords["y1"]
        x2 = crop_coords["x2"]
        y2 = crop_coords["y2"]
        img = img.crop((x1, y1, x2, y2))
        
    if size:
        size = int(size[0]), int(size[1])
        img = img.resize(size, Image.ANTIALIAS)
        
    # save to a different path so we don't modify the image in the given path
    tmp_path = image_path + str(randint(0, 999)).zfill(3)
    img.save(tmp_path, img_format)
    return tmp_path

def create_png(file_path, size=None, coords=None):
    """ 
    creates the given uploadedFile, which is a png image.
    """
    tmp_path = rescale(file_path, 'png', size, coords)
    res = parse("POST", 'files/' + BAD_FILE_CHR.sub('',
        file_path.split("/")[-1]), tmp_path , content_type="image/png") 
    # now delete the tmp path that was created
    os.remove(tmp_path)    
    return res

def delete_file(name, content_type):
    """ deletes the given file """   
    return parse("DELETE", 'files/' + name, content_type=content_type)

def cloud_call(func_name, params, timeout=None):
    """ Calls a cloud function with the name func_name and with
    the parameters params. """
    return parse("POST", "functions/" + func_name,
            params, timeout=timeout)
            
            
# These dont belong here...
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
    if not string:
        return ''
    return " ".join([word.capitalize() for word in string.split(" ")])
    
    





