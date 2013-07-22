from django.utils import timezone

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
        request.session['comet_time'] = timezone.now()
        return view_func(request, *args, **kwargs)

    return view
