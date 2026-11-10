from django.contrib import admin
from .models import (
    Vehiculo,
    DocumentoVehiculo,
    PautaMantencion,
    RegistroMantencion,
    RegistroKilometraje,
    ChecklistPreUso,
    CostoVehiculo,
    ConfiguracionFlota,
    LogAlertaFlota,
)


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("patente", "marca", "modelo", "anio", "tipo", "asignacion", "estado", "kilometraje_actual", "activo")
    list_filter = ("estado", "asignacion", "tipo", "activo")
    search_fields = ("patente", "marca", "modelo", "conductor_habitual")


@admin.register(DocumentoVehiculo)
class DocumentoVehiculoAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "tipo_documento", "nombre_personalizado", "fecha_vencimiento", "entidad_emisora")
    list_filter = ("tipo_documento", "fecha_vencimiento")
    search_fields = ("vehiculo__patente", "nombre_personalizado", "numero_documento_o_poliza")


@admin.register(PautaMantencion)
class PautaMantencionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "intervalo_km", "intervalo_meses", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(RegistroMantencion)
class RegistroMantencionAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "titulo", "tipo_servicio", "fecha", "kilometraje", "proximo_km", "costo")
    list_filter = ("tipo_servicio", "fecha")
    search_fields = ("vehiculo__patente", "titulo", "taller")


@admin.register(RegistroKilometraje)
class RegistroKilometrajeAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "kilometraje", "fecha", "conductor_o_responsable")
    list_filter = ("fecha",)
    search_fields = ("vehiculo__patente", "conductor_o_responsable")


@admin.register(ChecklistPreUso)
class ChecklistPreUsoAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "conductor", "fecha_hora", "kilometraje", "aprobado_para_circular")
    list_filter = ("aprobado_para_circular", "fecha_hora")
    search_fields = ("vehiculo__patente", "conductor")


@admin.register(CostoVehiculo)
class CostoVehiculoAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "tipo", "fecha", "monto", "litros", "proveedor")
    list_filter = ("tipo", "fecha")
    search_fields = ("vehiculo__patente", "proveedor", "numero_documento")


@admin.register(ConfiguracionFlota)
class ConfiguracionFlotaAdmin(admin.ModelAdmin):
    list_display = ("__str__", "activo", "ultimo_envio")


@admin.register(LogAlertaFlota)
class LogAlertaFlotaAdmin(admin.ModelAdmin):
    list_display = ("fecha_envio", "tipo", "etapa", "vehiculo", "exitoso")
    list_filter = ("tipo", "etapa", "exitoso", "fecha_envio")
    search_fields = ("vehiculo__patente", "destinatarios")
