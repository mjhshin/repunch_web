"""
GCM HTTP Sender.
"""

import requests, json

from repunch.settings import GCM_RECEIVE_KEY, GCM_RECEIVE_KEY_NAME,\
GCM_API_KEY

NON_DATA_PARAMS = (GCM_RECEIVE_KEY_NAME, 'repunch_receivers')
GCM_URL = "https://android.googleapis.com/gcm/send"

RECEIVER_BATCH_SIZE = 200

def gcm_send(postBody):
    """
    postBody format/example:
        
        {
            # Required content
            gcmrkey: "<<GCM_RECEIVE_KEY>>",
            repunch_receivers: [{
                "registration_id": "..."
                "<employee|patron>_id": "...",
            }, ...],
	        action: "com.repunch.retailer.PUNCH",
        
            # optional content (must be less than 4kb)
            optionalData1: False,
            optionalData2: 77,
            optionalData3: "hasjkf",
            optionalData4: [1,2,3],
            optionalData5: {1:1, 2:2},
        }
        
    See http://developer.android.com/google/gcm/server.html#params
    for more GCM parameters.
    
    Note that Google GCM Servers convert all data to string.
    """
    if str(postBody[GCM_RECEIVE_KEY_NAME]) != GCM_RECEIVE_KEY:
        return False
    
    receivers = postBody['repunch_receivers']
    if len(receivers) == 0:
        return True
        
    headers = {
        'UserAgent': "GCM-Server",
        'content-type': 'application/json',
        'Authorization': 'key=%s' % (GCM_API_KEY,),
    }
    
    data = { k:v for k,v in postBody.iteritems()
        if k not in NON_DATA_PARAMS }
    
    
    # its either all employee or patron
    if "employee_id" in receivers[0].keys():
        which_ids = "employee_ids"
    else:
        which_ids = "patron_ids"
        
    # chunk messages to make sure the employee_ids | patron_ids
    # do not end up exceeding the 4kb limit of a GCM push
    while len(receivers) > 0:
        registration_ids, extra_ids = [], []
        rec = receivers[:RECEIVER_BATCH_SIZE]
        receivers = rec
        for r in rec:
            registration_ids.append(r["registration_id"])
            extra_ids.append(r[which_ids])
            
        batch_data = data.copy()
        batch_data.update({which_ids: extra_ids})
    
        res = requests.post(GCM_URL, data=json.dumps({
            "registration_ids": registration_ids,
            "data": batch_data,
        }), headers=headers)
        
        # TODO handle response
        print res.json()
    
    
    return True
