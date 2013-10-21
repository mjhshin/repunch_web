"""
GCM HTTP Sender.
"""

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
    """
    pass
