#file use for helper functions for the repunch class
import calendar
from libs.dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime
from django.utils import timezone
from threading import Timer
import json, time, pytz, httplib, urllib

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
        start = start.replace(day=1, hour=0, minute=0, second=0)
    elif type == 'week-to-date':
        # from monday to sunday!
        start = start + relativedelta(days=-1*start.weekday())
    elif type == 'last-week':
        start = start + relativedelta(days=-1*start.weekday() - 7)
        end = start + relativedelta(days=7)
    elif type == 'last-month':
        start = start + relativedelta(days=-1*start.day)
        month_maxday = start.day
        # get first day of the month
        start = start + relativedelta(days=-1*start.day + 1)
        end = start.replace(day=month_maxday,
            hour=23, minute=59, second=59)
    
    return (start, end)

def set_timezone(request, tz=None):
    if not tz:
        tz = request.session.get('store_timezone') 
    else:
        request.session['store_timezone'] = tz
        
    if tz:
        timezone.activate(tz)
        
def get_map_data(address):
    """
    Expects address to be separated by spaces with no commas.
    
    Returns {"coordinates":(lat, lng), "neighborhood":"XXX"}
    Neighborhood may not be available.
    """
    conn = httplib.HTTPConnection("maps.googleapis.com")
    conn.request("GET", "/maps/api/geocode/json?%s&sensor=false" %\
        urllib.urlencode({"address":address}))
    map_data = {}
    resp = conn.getresponse()
    if resp.status == 200:
        data = json.loads(resp.read())
        
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            map_data['coordinates'] =\
                [location['lat'], location['lng']]
            # get the neighborhood if available
            for comp in\
                data['results'][0]["address_components"]:
                if "neighborhood" in comp['types']:
                    map_data['neighborhood'] = comp["short_name"]
                    break
        
    conn.close()
        
    return map_data
        
        
def get_timezone(zip_code):
    # first need to get the lat, lng
    conn = httplib.HTTPConnection("maps.googleapis.com")
    conn.request("GET", "/maps/api/geocode/json?address=%s&sensor=false" % str(zip_code))
    
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
    
    
def delete_after_delay(to_del, delay):
    def _delete():
        for each in to_del:
            each.delete()
    t = Timer(delay, _delete)
    t.start()
        
