from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .roles import is_analyst, is_editor


def analyst_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        if not is_analyst(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def editor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        if not is_editor(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
