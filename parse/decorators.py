from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from parse import session as SESSION

def access_required(view_func):
    """
    Logs out the user if he has an ACL of ACCESS_NONE.
    It is true that users with no access may not be able to log in.
    However, this decorator takes care of the care where a logged in
    user is stripped of access priviledge.
    
    *NOTE* that assumes that the user is logged in!
    """
    def view(request, *args, **kwargs):
        if SESSION.get_store(request.session).has_access(request.session['account']):
            return view_func(request, *args, **kwargs)
        else:
            return redirect(reverse("manage_logout"))

    return view
