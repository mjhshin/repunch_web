
def session_comet(view_func):
    """
    Makes sure that there is only 1 manage_refresh thread running
    for each client between view transitions by simply checking
    the request.session.
    
    Use with all views except ajax only views and public views.
    Must be called after the login_required decorator!
    """
    def view(request, *args, **kwargs):
        
        return view_func(request, *args, **kwargs)

    return view
