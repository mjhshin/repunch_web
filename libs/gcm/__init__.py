"""
GCM HTTP Sender.
"""

import requests, json

from repunch.settings import GCM_RECEIVE_KEY, GCM_RECEIVE_KEY_NAME,\
GCM_API_KEY_OLD, GCM_API_KEY_NEW

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
	        
	        # 1 to employ backwards compat. 0 otherwise.
	        # Default is 1.
            support: [1|0],
        
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
        
    if int(postBody.get("support", 1)) > 0:
        api_key = GCM_API_KEY_OLD
    else:
        api_key = GCM_API_KEY_NEW
        
    headers = {
        'UserAgent': "GCM-Server",
        'content-type': 'application/json',
        'Authorization': 'key=%s' % (api_key,),
    }
    
    data = { k:v for k,v in postBody.iteritems()
        if k not in NON_DATA_PARAMS }
    
    
    # its either all employee or patron
    if "employee_id" in receivers[0].keys():
        which_id = "employee_id"
    else:
        which_id = "patron_id"
        
    # chunk messages to make sure the employee_ids | patron_ids
    # do not end up exceeding the 4kb limit of a GCM push
    while len(receivers) > 0:
        registration_ids, extra_ids = [], []
        rec = receivers[:RECEIVER_BATCH_SIZE]
        receivers = receivers[len(rec):]
        
        """
        A test that this will never result in an infinite loop.
        receivers = [1,2,3,4,5,6,7,8,9,10]
        batch_count = 3
        while len(receivers) > 0:
            rec = receivers[:batch_count]
            print rec
            receivers = receivers[len(rec):]
        """
        
        for r in rec:
            registration_ids.append(r["registration_id"])
            extra_ids.append(r[which_id])
            
        batch_data = data.copy()
        batch_data.update({which_id+"s": extra_ids})
    
        res = requests.post(GCM_URL, data=json.dumps({
            "registration_ids": registration_ids,
            "data": batch_data,
        }), headers=headers)
        
        # TODO handle response
        # print res.json()
    
    
    return True
