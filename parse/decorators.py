from datetime import datetime

def session_comet(view_func):
    """
    Makes sure that there is only 1 manage_refresh thread running
    for each client between view transitions by simply checking
    the request.session.
    
    Use with ALL views EXCEPT ajax only views.
    """
    def view(request, *args, **kwargs):
        print "session_comet"
        request.session['comet_dead_time'] = timezone.now()
        return view_func(request, *args, **kwargs)

    return view
