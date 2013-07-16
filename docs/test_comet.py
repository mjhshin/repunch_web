from django.contrib.sessions.backends.cache import SessionStore
from parse.apps.stores.models import Store
from apps.comet.models import CometSession
import sys

def flag_go(session_key, obj):
    # get the latest redemption
    store = Store.objects().get(objectId="mF3Hox2QkU")
    if obj == "pendingRedemption":
        x = store.get("redeemRewards", limit=1,
            order="-createdAt")[0]
    elif obj == "newFeedback":
        x = store.get("receivedMessages", limit=1,
            order="-createdAt")[0]

    # update the session
    session = SessionStore(session_key)
    if obj not in session:
        session[obj] = [x.__dict__]
    else:
        session[obj].append(x.__dict__)
        
    session.save()

    # the GO code!
    CometSession.objects.update()
    comet_session = CometSession.objects.get(session_key=session_key)
    comet_session.modified = True
    comet_session.save()
