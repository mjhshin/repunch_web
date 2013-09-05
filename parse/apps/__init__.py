import json, httplib
from parse.apps.patrons.models import PunchCode
from repunch.settings import REST_CONNECTION_META, PARSE_BATCH_LIMIT

# Make sure that the PunchCode table exist. If not, create and populate.
# This could be run in different threads for speed but it is only done
# once so just keep it here.
def init_punch_codes():
    if not PunchCode.objects().get(punch_code='00000'):
        reqs, code, rcm = [], 0, REST_CONNECTION_META.copy()
        rcm["Content-Type"] = "application/json"
        while code < 100000:
            reqs.append({
                "method": "POST",
                    "path": "/1/classes/PunchCode",
                    "body": {
                         "punch_code": str(code).zfill(5),
                         "is_taken": False,
                         "username": None,
                    }
            })
            code += 1
            # send a request every PARSE_BATCH_LIMIT requests in the cache 
            if code % PARSE_BATCH_LIMIT == 0 or code == 99999:
                connection = httplib.HTTPSConnection('api.parse.com', 443)
                connection.connect()
                connection.request('POST', '/1/batch', json.dumps({
                       "requests": reqs, "limit":0 }), rcm)
                connection.getresponse().read()
                # clear the reqs
                reqs = []
                
# init_punch_codes

