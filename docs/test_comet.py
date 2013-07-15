from django.contrib.sessions.backends.cache import SessionStore
from parse.apps.stores.models import Store
from apps.comet.models import CometSession
import sys

def flag_go(session_key):
    # get the latest redemption
    store = Store.objects().get(objectId="mF3Hox2QkU")
    newest_redemption = store.get("redeemRewards", limit=1,
        order="-createdAt")[0]

    # update the session
    session = SessionStore(session_key)
    if "pendingRedemption" not in session:
        session["pendingRedemption"] = [newest_redemption.__dict__]
    else:
        session["pendingRedemption"].append(newest_redemption.__dict__)
        
    session.save()

    # the GO code!
    CometSession.objects.update()
    comet_session = CometSession.objects.get(session_key=session_key)
    comet_session.modified = True
    comet_session.save()
