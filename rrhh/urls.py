from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_rrhh, name="rrhh_dashboard"),
    path("empleados/", views.lista_empleados, name="rrhh_lista_empleados"),
    path("empleados/<int:pk>/", views.detalle_empleado, name="rrhh_detalle_empleado"),
    path("empleados/<int:pk>/editar/", views.editar_empleado, name="rrhh_editar_empleado"),
    path("ausencias/", views.lista_ausencias, name="rrhh_ausencias"),
    path("documentos/<int:pk>/editar/", views.editar_documento, name="rrhh_editar_documento"),
    path("documentos/<int:pk>/eliminar/", views.eliminar_documento, name="rrhh_eliminar_documento"),
    path("exportar/excel/", views.exportar_nomina_excel, name="rrhh_exportar_excel"),
    
    # Gastos de RRHH
    path("gastos/", views.lista_gastos_rrhh, name="rrhh_gastos"),
    path("gastos/exportar/", views.exportar_gastos_excel, name="rrhh_exportar_gastos"),
    
    # Inventario EPP / Ropa de RRHH
    path("inventario/", views.inventario_epp, name="rrhh_inventario"),
    path("inventario/ingreso/", views.registrar_ingreso_epp, name="rrhh_registrar_ingreso_epp"),
    path("inventario/entrega/", views.registrar_entrega_epp, name="rrhh_registrar_entrega_epp"),
]
