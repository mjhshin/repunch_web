import json, httplib, random
from parse.apps.patrons.models import PunchCode
from repunch.settings import REST_CONNECTION_META, PARSE_BATCH_LIMIT

# Make sure that the PunchCode table exist. If not, create and populate.
# This could be run in different threads for speed but it is only done
# once so just keep it here.
def init_punch_codes():
    # build the list of all possible codes 00000 - 99999
    punch_codes = [str(code).zfill(5) for code in range(0,100000)]
    rcm = REST_CONNECTION_META.copy()
    rcm["Content-Type"] = "application/json"
    
    while len(punch_codes) > 0:
        reqs = []
        while len(reqs) < 50 and len(punch_codes) > 0:
            pc =\
                punch_codes.pop(random.randint(0, len(punch_codes)-1))
            reqs.append({
                "method": "POST",
                    "path": "/1/classes/PunchCode",
                    "body": {
                         "punch_code": pc,
                         "is_taken": False,
                         "username": None,
                    }
            })
            
        # send a request every PARSE_BATCH_LIMIT requests in the cache 
        connection = httplib.HTTPSConnection('api.parse.com', 443)
        connection.connect()
        connection.request('POST', '/1/batch', json.dumps({
               "requests": reqs, "limit":0 }), rcm)
        connection.getresponse().read()
        print len(punch_codes)
                
# init_punch_codes()

