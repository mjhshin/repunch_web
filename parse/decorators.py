from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from repunch.settings import COMET_DIE_TIME

def session_comet(view_func):
    """
    Makes sure that there is only 1 manage_refresh thread running
    for each client between view transitions by simply checking
    the request.session.
    
    Use with ALL views EXCEPT ajax only views.
    This will ensure that all dangling manage_refresh processes will
    die. This assumes that the cloud_call 
    """
    def view(request, *args, **kwargs):
        # insert into session the time the page got accessed
        comet_time = timezone.now()
        request.session['comet_time'] = comet_time
        request.session['comet_die_time'] = comet_time +\
            relativedelta(seconds=COMET_DIE_TIME)
        # need to save it here so that other looping requests know
        request.session.save()
        return view_func(request, *args, **kwargs)

    return view
