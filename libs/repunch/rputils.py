#file use for helper functions for the repunch class
import string, random, calendar
from datetime import timedelta, datetime
from django.utils import timezone
from PIL import Image
import json, time, pytz

from parse.apps.accounts.models import Settings

# function for generating unique ID for retailer
def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
    gid = ''.join(random.choice(chars) for x in range(size))
    
    #make sure this is a unique ID
    if Settings.objects().count(retailer_id=gid) == 0:
        return gid
    
    return generate_id()
    

def rescale(image_path, width=100, height=100):
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
        
    img = img.crop((int(x_offset), int(y_offset), int(x_offset+crop_width), int(y_offset+crop_height)))
    img = img.resize((int(dst_width), int(dst_height)), Image.ANTIALIAS)
        
    img.save(image_path)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+1):
        yield start_date + timedelta(n)
        
def calculate_daterange(type):
    start = datetime.now()
    end = datetime.now()
    
    #default to today
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end.replace(hour=23, minute=59, second=59, microsecond=0)
    
    if type == 'month-to-date':
        start = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif type == 'week-to-date':
        day = calendar.weekday(start.year, start.month, start.day)
        start = start - timedelta(days=day)
    elif type == 'last-week':
        #get the day of te week
        day = calendar.weekday(start.year, start.month, start.day)
        start = start - timedelta(days=(day+7)) #go back to the start of last week
        end = start + timedelta(days=6) # now go to the end of the week
    elif type == 'last-month':
        #first day of current month
        start = start.replace(day=1)
        start = start - timedelta(days=1) # go back one day to previous month
        start = start.replace(day=1) # first day of the month
        
        #calculate last day of mont
        (_, last_day) = calendar.monthrange(start.year, start.month)
        end = start #need to start from her in case it is a different year
        end = end.replace(day=last_day, hour=23, minute=59, second=59, microsecond=0)
    
    return (start, end)

def set_timezone(request, tz=None):
    if tz == None:
        tz = request.session.get('django_timezone') # if this isn't set, just default to default
    else:
        request.session['django_timezone'] = tz
        
    if tz:
        timezone.activate(tz)
        
def get_timezone(zip_code):
    import httplib
    
    # first need to get the lat, lng
    conn = httplib.HTTPConnection("maps.googleapis.com")
    conn.request("GET", "/maps/api/geocode/json?address=%s&sensor=false" % zip_code)
    
    resp = conn.getresponse()
    if resp.status == 200:
        data = json.loads(resp.read())
        conn.close();
        
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            
            #get timezone based on geolocation
            conn = httplib.HTTPSConnection("maps.googleapis.com")
            conn.request("GET", "/maps/api/timezone/json?location=%s,%s&timestamp=%s&sensor=false" % (location['lat'], location['lng'], time.mktime(datetime.utcnow().timetuple())))
            
            resp = conn.getresponse()
            if resp.status == 200:
                data = json.loads(resp.read())
                if data['status'] == 'OK':
                    try:
                        return pytz.timezone(data['timeZoneId'])
                    except Exception:
                        pass # don't do anythin we will just use the default
    else:
        conn.close()
        
    return pytz.timezone(timezone.get_default_timezone_name())
        
