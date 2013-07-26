from django.contrib.sessions.backends.cache import SessionStore
from parse.apps.stores.models import Store
from apps.comet.models import CometSession
from repunch.settings import COMET_REQUEST_RECEIVE,\
COMET_RECEIVE_KEY_NAME, COMET_RECEIVE_KEY
import sys, requests, json

def flag_go(obj):
    # get the latest redemption
    store = Store.objects().get(objectId="mF3Hox2QkU")
    if obj == "pendingRedemption":
        x = store.get("redeemRewards", limit=1,
            order="-createdAt")[0]
    elif obj == "newFeedback":
        x = store.get("receivedMessages", limit=1,
            order="-createdAt")[0]
    elif obj == "newMessage":
        x = store.get("sentMessages", limit=1,
            order="-createdAt")[0]

    # make the post request
    payload = {
        COMET_RECEIVE_KEY_NAME:COMET_RECEIVE_KEY,
        obj:x.jsonify()
    }
    requests.post(COMET_REQUEST_RECEIVE + store.objectId,
        data=json.dumps(payload))
