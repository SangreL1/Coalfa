from django.contrib import admin
from .models import Empleado, PeriodoAusencia, Documento


class AusenciaInline(admin.TabularInline):
    model = PeriodoAusencia
    extra = 0
    fields = ("tipo", "fecha_inicio", "fecha_fin", "descripcion")


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    fields = ("tipo", "descripcion", "archivo", "fecha_subida")
    readonly_fields = ("fecha_subida",)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "rut", "cargo", "area", "estado", "fecha_ingreso")
    list_filter = ("estado", "area", "cargo")
    search_fields = ("nombre", "apellido", "rut")
    inlines = [AusenciaInline, DocumentoInline]
    fieldsets = (
        ("Identificación", {"fields": ("nombre", "apellido", "rut", "foto")}),
        ("Cargo y Área", {"fields": ("cargo", "area", "fecha_ingreso")}),
        ("Estado Laboral", {"fields": ("estado",)}),
        ("Contacto", {"fields": ("email", "telefono")}),
    )


@admin.register(PeriodoAusencia)
class PeriodoAusenciaAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tipo", "fecha_inicio", "fecha_fin")
    list_filter = ("tipo",)
    search_fields = ("empleado__nombre", "empleado__apellido")


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tipo", "descripcion", "fecha_subida")
    list_filter = ("tipo", "fecha_subida")
    search_fields = ("empleado__nombre", "empleado__apellido")
