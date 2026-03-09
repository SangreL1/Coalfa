from django.contrib import admin
from .models import Proveedor, Producto, Lote, MovimientoTrazabilidad, RegistroServicio


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "rut", "contacto", "telefono")
    search_fields = ("nombre", "rut")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "unidad_medida", "temperatura_min", "temperatura_max")
    search_fields = ("nombre",)


class MovimientoInline(admin.TabularInline):
    model = MovimientoTrazabilidad
    extra = 0
    readonly_fields = ("desde", "hacia", "fecha", "responsable", "observaciones")
    can_delete = False


class ServicioInline(admin.TabularInline):
    model = RegistroServicio
    extra = 0
    readonly_fields = ("cantidad_servida", "responsable", "fecha", "observaciones")
    can_delete = False


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = (
        "numero_lote", "producto", "proveedor", "ubicacion_actual",
        "estado", "fecha_vencimiento", "cantidad",
    )
    list_filter = ("ubicacion_actual", "estado", "proceso", "producto", "proveedor")
    search_fields = ("numero_lote", "producto__nombre", "numero_lote_proveedor", "numero_guia")
    filter_horizontal = ("lotes_padres",)
    inlines = [MovimientoInline, ServicioInline]
    fieldsets = (
        ("Identificación", {
            "fields": ("numero_lote", "producto", "proveedor",
                       "numero_lote_proveedor", "numero_guia")
        }),
        ("Cantidades y Fechas", {
            "fields": ("cantidad", "fecha_recepcion", "fecha_vencimiento")
        }),
        ("Control Sanitario", {
            "fields": ("temperatura_recepcion", "proceso")
        }),
        ("Trazabilidad", {
            "fields": ("lotes_padres",)
        }),
        ("Estado y Ubicación", {
            "fields": ("ubicacion_actual", "estado", "responsable_registro", "observaciones")
        }),
    )


@admin.register(MovimientoTrazabilidad)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ("lote", "desde", "hacia", "fecha", "responsable")
    list_filter = ("desde", "hacia")
    readonly_fields = ("lote", "desde", "hacia", "fecha", "responsable")


@admin.register(RegistroServicio)
class RegistroServicioAdmin(admin.ModelAdmin):
    list_display = ("lote", "cantidad_servida", "responsable", "fecha")
    list_filter = ("fecha",)
    readonly_fields = ("lote", "cantidad_servida", "responsable", "fecha", "observaciones")
