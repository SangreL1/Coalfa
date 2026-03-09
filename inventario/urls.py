from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_inventario, name="inventario_dashboard"),
    path("mapa/", views.mapa_bodega, name="inventario_mapa_bodega"),
    path("temperatura/registrar/", views.registrar_temperatura, name="inventario_registrar_temperatura"),
    path("lotes/", views.lista_lotes, name="inventario_lista_lotes"),
    path("lotes/<int:pk>/", views.detalle_lote, name="inventario_detalle_lote"),
    path("lotes/<int:pk>/editar/", views.editar_lote, name="inventario_editar_lote"),
    path("lotes/<int:lote_id>/mover/<str:nueva_ubicacion>/", views.mover_lote, name="inventario_mover_lote"),
    path("lotes/<int:pk>/eliminar/", views.eliminar_lote, name="inventario_eliminar_lote"),
    path("alertas/", views.alertas_vencimiento, name="inventario_alertas"),
    # Trazabilidad
    path("recibir/", views.recibir_lote, name="inventario_recibir_lote"),
    path("transformar/", views.transformar_lote, name="inventario_transformar_lote"),
    path("exportar/csv/", views.exportar_inventario_csv, name="exportar_inventario_csv"),
    path("exportar/excel/", views.exportar_inventario_excel, name="exportar_inventario_excel"),
    path("exportar/pdf/", views.generar_reporte_pdf, name="generar_reporte_pdf"),
    path("lotes/<int:pk>/servicio/", views.registrar_servicio, name="inventario_registrar_servicio"),
    path("lotes/<int:pk>/trazabilidad/", views.trazabilidad_lote, name="inventario_trazabilidad_lote"),
    # Productos
    path("productos/", views.lista_productos, name="inventario_lista_productos"),
    path("productos/<int:pk>/eliminar/", views.eliminar_producto, name="inventario_eliminar_producto"),
    # Tareas (to-do)
    path("tareas/agregar/", views.tarea_agregar, name="inventario_tarea_agregar"),
    path("tareas/<int:pk>/toggle/", views.tarea_toggle, name="inventario_tarea_toggle"),
    path("tareas/<int:pk>/eliminar/", views.tarea_eliminar, name="inventario_tarea_eliminar"),
]
