from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def audit_read_only(view_func):
    """Decorador estricto para bloquear por completo vistas de acción/modificación a usuarios con rol AUDITOR."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol == "AUDITOR":
            messages.error(
                request,
                "🔒 Acción no permitida: Tu usuario tiene el rol 'Auditor (Solo Lectura)'. "
                "No tienes permisos para agregar, modificar, mover o eliminar datos."
            )
            referrer = request.META.get("HTTP_REFERER")
            if referrer and request.path not in referrer:
                return redirect(referrer)
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped


def rrhh_required(view_func):
    """Allow RRHH, ADMIN, GERENTE and AUDITOR (read-only) users."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.rol not in ("RRHH", "ADMIN", "GERENTE", "AUDITOR"):
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("dashboard")
        if request.user.rol == "AUDITOR" and request.method == "POST":
            messages.error(
                request,
                "🔒 Acción no permitida: Tu usuario tiene el rol 'Auditor (Solo Lectura)'. "
                "No tienes permisos para realizar modificaciones, agregar o eliminar información."
            )
            referrer = request.META.get("HTTP_REFERER")
            if referrer and request.path not in referrer:
                return redirect(referrer)
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped


def operacional_required(view_func):
    """Allow OPERACIONAL, ADMIN, GERENTE and AUDITOR (read-only) users."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.rol not in ("OPERACIONAL", "ADMIN", "GERENTE", "AUDITOR"):
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("dashboard")
        if request.user.rol == "AUDITOR" and request.method == "POST":
            messages.error(
                request,
                "🔒 Acción no permitida: Tu usuario tiene el rol 'Auditor (Solo Lectura)'. "
                "No tienes permisos para realizar modificaciones, agregar o eliminar información."
            )
            referrer = request.META.get("HTTP_REFERER")
            if referrer and request.path not in referrer:
                return redirect(referrer)
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped

