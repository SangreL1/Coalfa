from django.contrib import admin
from .models import (
    Rol,
    PerfilUsuario,
    Especialidad,
    Medico,
    Paciente,
    FichaMedica,
    VisitaAtencion,
)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ("nombre",)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "rut")
    filter_horizontal = ("especialidades", "roles")


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("rut", "get_full_name", "fecha_nacimiento")
    search_fields = ("rut", "user__last_name", "user__first_name")

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.short_description = "Nombre completo"


# Opcional: El admin técnico puede ver esto, pero el admin de negocio NO debería.
# Se registra para desarrollo.
admin.site.register(FichaMedica)
admin.site.register(VisitaAtencion)
