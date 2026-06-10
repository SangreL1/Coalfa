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
    # Reportes de Consumo
    path("consumo/", views.resumen_consumo, name="inventario_resumen_consumo"),
    path("consumo/exportar/", views.exportar_consumo_excel, name="inventario_exportar_consumo_excel"),
    # Carga Masiva y Facturas
    path("importar/solicitudes/", views.cargar_solicitudes_excel, name="inventario_cargar_excel"),
    path("facturas/", views.gestionar_facturas, name="inventario_gestionar_facturas"),
    path("facturas/procesar/<str:filename>/", views.procesar_factura_pdf, name="inventario_procesar_factura_pdf"),
    path("facturas/ver/<str:filename>/", views.ver_factura_pdf, name="inventario_ver_factura_pdf"),
    path("facturas/eliminar/<str:filename>/", views.eliminar_factura_pdf, name="inventario_eliminar_factura_pdf"),
    path("facturas/eliminar-todas/", views.eliminar_todas_facturas, name="inventario_eliminar_todas_facturas"),
    path("facturas/confirmar/", views.confirmar_carga_factura, name="inventario_confirmar_carga_factura"),
    path("despacho-rapido/", views.despacho_rapido, name="inventario_despacho_rapido"),
]
