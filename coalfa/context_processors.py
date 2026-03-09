from .models import Usuario


def solicitudes_pendientes(request):
    """Inyecta el conteo de solicitudes pendientes en todos los templates (solo para ADMIN)."""
    if request.user.is_authenticated and getattr(request.user, 'rol', None) == 'ADMIN':
        count = Usuario.objects.filter(solicitud_pendiente=True).count()
        return {'solicitudes_count': count}
    return {}
