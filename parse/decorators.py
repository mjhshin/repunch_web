from django.shortcuts import redirect
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.decorators import available_attrs
from functools import wraps

from parse import session as SESSION

def access_required(view_func):
    """
    Logs out the user if he has an ACL of ACCESS_NONE.
    It is true that users with no access may not be able to log in.
    However, this decorator takes care of the case where a logged in
    user's ACL is changed to ACCESS_NONE.
    
    This decorator should only be used on views that return an
    HttpResponse/rendered page - not redirects or if done with ajax.
    
    *NOTE* that assumes that the user is logged in!
    """
    def decorator(request, *args, **kwargs):
        if SESSION.get_store(request.session).has_access(request.session['account']):
            return view_func(request, *args, **kwargs)
        else:
            return redirect(reverse("manage_logout"))
    return decorator
    
def _admin_only(reverse_url, except_method):
    """
    Redirects the user to the given reverse_url if not admin.
    The user will not be redirected if the request.method is in
    except_method, which is a tuple with possible values GET &| POST.
    This will raise an Http404 if reverse_url is None.
    
    *NOTE* that assumes that the user is logged in!
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if SESSION.get_store(request.session).is_admin(\
                request.session['account']) or (except_method and\
                request.method in except_method):
                return view_func(request, *args, **kwargs)
            else:
                if reverse_url:
                    return redirect(reverse(reverse_url))
                else:
                    raise Http404
        return _wrapped_view
    return decorator


def admin_only(function=None, reverse_url=None, except_method=None):
    """
    Redirects the user to the given reverse_url if not admin.
    This will raise an Http404 if reverse_url is None.
    
    *NOTE* that assumes that the user is logged in!
    """
    
    actual_decorator = _admin_only(
        reverse_url=reverse_url,
        except_method=except_method
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
