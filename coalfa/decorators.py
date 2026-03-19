from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def rrhh_required(view_func):
    """Allow only RRHH and ADMIN users."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.rol not in ("RRHH", "ADMIN", "GERENTE"):
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped


def operacional_required(view_func):
    """Allow only OPERACIONAL and ADMIN users."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.rol not in ("OPERACIONAL", "ADMIN", "GERENTE"):
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped
