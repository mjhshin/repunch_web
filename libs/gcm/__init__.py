"""
GCM HTTP Sender.
"""

import requests, json

from repunch.settings import GCM_RECEIVE_KEY, GCM_RECEIVE_KEY_NAME,\
GCM_API_KEY

NON_DATA_PARAMS = (GCM_RECEIVE_KEY_NAME, 'registration_ids', 'action')
GCM_URL = "https://android.googleapis.com/gcm/send"

def gcm_send(postBody):
    """
    postBody format/example:
        
        {
            # Required content
            gcmrkey: "<<GCM_RECEIVE_KEY>>",
            registration_ids: ["kh7x7towm4t", "uytxgygx", ...],
	        action: "com.repunch.retailer.PUNCH"
        
            # optional content (must be less than 4kb)
            optionalData1: False,
            optionalData2: 77,
            optionalData3: "hasjkf",
            optionalData4: [1,2,3],
            optionalData5: {1:1, 2:2},
        }
        
    See http://developer.android.com/google/gcm/server.html#params
    for more GCM parameters.
    """
    if str(postBody[GCM_RECEIVE_KEY_NAME]) != GCM_RECEIVE_KEY:
        return False
    
    headers = {
        'UserAgent': "GCM-Server",
        'content-type': 'application/json',
        'Authorization': 'key=%s' % (GCM_API_KEY,),
    }
    payload = {
        "registration_ids": postBody['registration_ids'],
        "data": { k:v for k,v in postBody.iteritems()
            if k not in NON_DATA_PARAMS },
    }
    
    res = requests.post(GCM_URL, data=json.dumps(payload),
        headers=headers)
    
    # TODO handle response
    print res.json()
    
    
    return res.ok
