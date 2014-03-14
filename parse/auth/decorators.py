"""
A modified version of django.contrib.auth.decorators.login_required
"""

import urlparse, json
from functools import wraps
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.contrib.sessions.backends.cache import SessionStore
from django.contrib.auth import REDIRECT_FIELD_NAME, SESSION_KEY
from django.utils.decorators import available_attrs

from parse import session as SESSION
from parse.auth import logout
from repunch.settings import LOGIN_URL_DEV, PRODUCTION_SERVER,\
DEVELOPMENT_TOKEN

def user_passes_test(test_func, login_url, redirect_field_name,
    http_response, content_type):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    
    This also sets the timezone to the store's timezone.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                if SESSION.get_store(request.session) and\
                    SESSION.get_store(request.session).active:
                    # may not want to import parse.session here due
                    # to cyclic imports
                    timezone.activate(SESSION.get_store_timezone(\
                        request.session))
                    try:
                        return view_func(request, *args, **kwargs)
                    except KeyError:
                        return logout(request, "manage_login")
                else:
                    return logout(request, "manage_login")
                
            # if http_response is provided and content_type is json
            # and request.is_ajax then this request if from comet.js
            if request.is_ajax() and http_response and\
                content_type == "application/json":
                # no need to update session- if it got here then the session is empty
                #request.session.clear()
                #request.session.update(SessionStore(request.session.session_key))
                return HttpResponse(json.dumps(http_response),
                    content_type=content_type)
                
            path = request.build_absolute_uri()
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse.urlparse(login_url or
                                                        settings.LOGIN_URL)[:2]
            current_scheme, current_netloc = urlparse.urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            # no need to update session- if it got here then the session is empty
            #request.session.clear()
            #request.session.update(SessionStore(request.session.session_key))
            return redirect_to_login(path, login_url, redirect_field_name)
        return _wrapped_view
    return decorator


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None,
    http_response=None, content_type="application/json"):
    """
    Decorator for views that checks that the user is logged in,
    redirecting to the log-in page if necessary.

    The key difference b/w this and the original Django implementation
    is that the test for authentication is now using the sessionToken
    retrieved from Parse.
    
    This also does a couple of things:
        - sets the timezone to the store's timezone
        - if the store's active field is set to False, the user is logged out
        - if a KeyError occurs, the user is logged out
    """
    actual_decorator = user_passes_test(
        lambda req: req.session.get('account') and\
                    req.session.get(SESSION_KEY),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        http_response=http_response,
        content_type=content_type,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
    
    
#####################################
def dev_passes_test(test_func, login_url, redirect_field_name,
    http_response, content_type):
    """
    Used for preventing non-repunch engineers from accessing all pages
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
                
            if request.is_ajax() and http_response and\
                content_type == "application/json":
                return HttpResponse(json.dumps(http_response),
                    content_type=content_type)    
            
            path = request.build_absolute_uri()
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse.urlparse(login_url or
                                                        settings.LOGIN_URL)[:2]
            current_scheme, current_netloc = urlparse.urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            # no need to update session- if it got here then the session is empty
            #request.session.clear()
            #request.session.update(SessionStore(request.session.session_key))
            return redirect_to_login(path, login_url, redirect_field_name)
        return _wrapped_view
    return decorator


def dev_login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=LOGIN_URL_DEV,
    http_response=None, content_type="application/json"):
    """
    Used for preventing non-repunch engineers from accessing any page.
    This does nothing if PRODUCTION_SERVER is True.
    """
    if PRODUCTION_SERVER:
        actual_decorator = dev_passes_test(
            lambda req: True,
            login_url=login_url,
            redirect_field_name=redirect_field_name,
            http_response=http_response,
            content_type=content_type,
        )
    else:
        actual_decorator = dev_passes_test(
            lambda req: req.session.get(DEVELOPMENT_TOKEN),
            login_url=login_url,
            redirect_field_name=redirect_field_name,
            http_response=http_response,
            content_type=content_type,
        )
    
    if function:
        return actual_decorator(function)
    return actual_decorator

def _dev_only(raise_404):
    """
    Raises a http_404 if PRODUCTION_SERVER is True.
    """
    def _dev_only_decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if raise_404:
                raise Http404
            else:
                return view_func(request, *args, **kwargs)
                    
        return _wrapped_view
        
    return _dev_only_decorator


def dev_only(function=None):
    """
    Raises a http_404 if PRODUCTION_SERVER is True.
    """
    actual_decorator = _dev_only(raise_404=PRODUCTION_SERVER)
    if function:
        return actual_decorator(function)
    return actual_decorator
    
