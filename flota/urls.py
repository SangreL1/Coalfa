from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & General
    path("", views.dashboard_flota, name="flota_dashboard"),

    # Vehículos
    path("vehiculos/", views.lista_vehiculos, name="flota_lista_vehiculos"),
    path("vehiculos/nuevo/", views.crear_vehiculo, name="flota_crear_vehiculo"),
    path("vehiculos/<int:pk>/", views.detalle_vehiculo, name="flota_detalle_vehiculo"),
    path("vehiculos/<int:pk>/editar/", views.editar_vehiculo, name="flota_editar_vehiculo"),
    path("vehiculos/<int:pk>/eliminar/", views.eliminar_vehiculo, name="flota_eliminar_vehiculo"),

    # Documentos con vencimiento
    path("documentos/nuevo/", views.agregar_documento, name="flota_agregar_documento"),
    path("vehiculos/<int:vehiculo_id>/documentos/nuevo/", views.agregar_documento, name="flota_agregar_documento_vehiculo"),
    path("documentos/<int:pk>/editar/", views.editar_documento, name="flota_editar_documento"),
    path("documentos/<int:pk>/eliminar/", views.eliminar_documento, name="flota_eliminar_documento"),

    # Mantenciones
    path("mantenciones/", views.lista_mantenciones, name="flota_mantenciones"),
    path("mantenciones/nueva/", views.agregar_mantencion, name="flota_agregar_mantencion"),
    path("vehiculos/<int:vehiculo_id>/mantenciones/nueva/", views.agregar_mantencion, name="flota_agregar_mantencion_vehiculo"),
    path("mantenciones/<int:pk>/eliminar/", views.eliminar_mantencion, name="flota_eliminar_mantencion"),

    # Pautas de mantención
    path("pautas/", views.pautas_mantencion, name="flota_pautas"),
    path("pautas/<int:pk>/eliminar/", views.eliminar_pauta, name="flota_eliminar_pauta"),

    # Odómetro / Kilometraje
    path("kilometraje/express/", views.registrar_kilometraje_express, name="flota_registro_km_express"),

    # Checklist pre-uso
    path("checklist/", views.checklist_preuso, name="flota_checklist_preuso"),
    path("vehiculos/<int:vehiculo_id>/checklist/", views.checklist_preuso, name="flota_checklist_preuso_vehiculo"),
    path("checklists/", views.lista_checklists, name="flota_lista_checklists"),

    # Costos & Combustible
    path("costos/", views.lista_costos, name="flota_lista_costos"),
    path("costos/nuevo/", views.agregar_costo, name="flota_agregar_costo"),
    path("vehiculos/<int:vehiculo_id>/costos/nuevo/", views.agregar_costo, name="flota_agregar_costo_vehiculo"),
    path("costos/<int:pk>/eliminar/", views.eliminar_costo, name="flota_eliminar_costo"),

    # Alertas y Notificaciones por Correo
    path("alertas/", views.panel_alertas, name="flota_panel_alertas"),
    path("alertas/configuracion/", views.configuracion_alertas, name="flota_configuracion_alertas"),
    path("alertas/disparar/", views.disparar_alertas_ahora, name="flota_disparar_alertas"),
    path("alertas/probar/", views.enviar_correo_prueba, name="flota_probar_correo"),
]
