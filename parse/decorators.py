from django.shortcuts import redirect
from django.http import Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.decorators import available_attrs
from functools import wraps
from urllib import urlencode
import json

from parse import session as SESSION

def _access_required(http_response, content_type):
    """
    Logs out the user if he has an ACL of ACCESS_NONE or the store
    is not active.
    It is true that users with no access may not be able to log in.
    However, this decorator takes care of the case where a logged in
    user's ACL is changed to ACCESS_NONE or if the store's active
    field has been set to False
    
    This decorator should only be used on views that return an
    HttpResponse/rendered page - not redirects or if done with ajax.
    
    *NOTE* that assumes that the user is logged in!
    """
    def _access_required_decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            store = SESSION.get_store(request.session)
            if store.has_access(request.session['account']) and\
                store.active:
                return view_func(request, *args, **kwargs)
            else:
                if http_response:
                    resp = http_response
                    if content_type == "application/json":
                        resp = json.dumps(http_response)
                    return HttpResponse(resp, content_type=content_type)
                else:
                    return redirect(reverse("manage_logout"))
        return _wrapped_view
    return _access_required_decorator


def access_required(function=None, http_response=None, content_type="application/json"):
    """
    Logs out the user if he has an ACL of ACCESS_NONE.
    It is true that users with no access may not be able to log in.
    However, this decorator takes care of the case where a logged in
    user's ACL is changed to ACCESS_NONE.
    
    Ajax returns should return an http_reponse of something so that
    a redirect to logout won't be executed. 
    
    *NOTE* that assumes that the user is logged in!
    *NOTE* there is no need to use this decorator if the _admin_only
    decorator is used in the same view because the admin_only decorator
    will cause redirects to views using this decorator if ACL changes or
    ACL of user is not admin to begin with =)
    """
    actual_decorator = _access_required(
        http_response=http_response,
        content_type=content_type
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
    
    
def _admin_only(reverse_url, reverse_postfix, except_method,
    http_response, content_type):
    """
    Redirects the user to the given reverse_url if not admin.
    The user will not be redirected if the request.method is in
    except_method, which is a tuple with possible values GET &| POST.
    This will raise an Http404 if reverse_url is None.
    
    *NOTE* that assumes that the user is logged in!
    """
    def _admin_only_decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if SESSION.get_store(request.session).is_admin(\
                request.session['account']) or (except_method and\
                request.method in except_method):
                return view_func(request, *args, **kwargs)
            else:
                if reverse_url:
                    reversed_url = reverse(reverse_url) + "?%s" %\
                        urlencode({'error': "Permission denied"})
                    
                    if reverse_postfix:
                        reversed_url =\
                            reversed_url + "&" + reverse_postfix
                    return redirect(reversed_url)
                elif http_response:
                    resp = http_response
                    if content_type == "application/json":
                        resp = json.dumps(http_response)
                    return HttpResponse(resp, content_type=content_type)
                else:
                    raise Http404
        return _wrapped_view
    return _admin_only_decorator


def admin_only(function=None, reverse_url=None, reverse_postfix=None,
    except_method=None, http_response=None, content_type="application/json"):
    """
    If user is not adming, redirects to the given reverse_url (if provided)
    or returns an http_response (if provided).
    If reverse_url or http_response is not given, an Http404 is raised.
    
    *NOTE* that only reverse_url or http_response should be provided!
    *NOTE* that assumes that the user is logged in!
    """
    actual_decorator = _admin_only(
        reverse_url=reverse_url,
        reverse_postfix=reverse_postfix,
        except_method=except_method,
        http_response=http_response,
        content_type=content_type
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
