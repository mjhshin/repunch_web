from django.utils import timezone

from libs.dateutil.relativedelta import relativedelta
from repunch.settings import COMET_REFRESH_RATE

# TODO MAKE USABLE (does nothing at the moment)
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
        """
        request.session['comet_dead_time'] =\
            timezone.now() + relativedelta(COMET_REFRESH_RATE+2)
        # so for 17 seconds, all calls to retailer refresh will 
        # return a server error in the ajax side.
        """
        return view_func(request, *args, **kwargs)

    return view
