from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    # --- Flujo Médico ---
    path("medico/dashboard/", views.dashboard_medico, name="dashboard_medico"),
    path("medico/buscar_paciente/", views.buscar_paciente, name="buscar_paciente"),
    path(
        "medico/paciente/registrar/",
        views.registrar_paciente,
        name="registrar_paciente",
    ),
    path("medico/ficha/<int:paciente_id>/", views.ver_ficha, name="ver_ficha"),
    path(
        "medico/ficha/editar/<int:paciente_id>/",
        views.editar_ficha,
        name="editar_ficha",
    ),
    path(
        "medico/atencion/nueva/<int:paciente_id>/",
        views.crear_atencion,
        name="crear_atencion",
    ),
    # --- Flujo gestion (Gestión de Médicos) ---
    path("gestion/medicos/", views.lista_medicos, name="lista_medicos"),
    path("gestion/medicos/crear/", views.crear_medico, name="crear_medico"),
    path("gestion/medicos/editar/<int:pk>/", views.update_medico, name="update_medico"),
    path(
        "gestion/medicos/eliminar/<int:pk>/", views.delete_medico, name="delete_medico"
    ),
    path("medicos/lista/", views.lista_medicos, name="lista"),
    # --- Gestión de Medicamentos (Admin) ---
    path("gestion/medicamentos/", views.lista_medicamentos, name="lista_medicamentos"),
    path(
        "gestion/medicamentos/crear/", views.crear_medicamento, name="crear_medicamento"
    ),
    path(
        "gestion/medicamentos/editar/<int:pk>/",
        views.update_medicamento,
        name="update_medicamento",
    ),
    path(
        "gestion/medicamentos/eliminar/<int:pk>/",
        views.delete_medicamento,
        name="delete_medicamento",
    ),
    # --- Gestión de Exámenes (Admin) ---
    path("gestion/examenes/", views.lista_examenes, name="lista_examenes"),
    path("gestion/examenes/crear/", views.crear_examen, name="crear_examen"),
    path(
        "gestion/examenes/editar/<int:pk>/", views.update_examen, name="update_examen"
    ),
    path(
        "gestion/examenes/eliminar/<int:pk>/", views.delete_examen, name="delete_examen"
    ),
    # --- Buscar Medicamentos ---
    path("buscar_medicamentos/", views.buscar_medicamentos, name="buscar_medicamentos"),
    # --- Gestión de Especialidades (Admin) ---
    path(
        "gestion/especialidades/",
        views.lista_especialidades,
        name="lista_especialidades",
    ),
    path(
        "gestion/especialidades/crear/",
        views.crear_especialidad,
        name="crear_especialidad",
    ),
    path(
        "gestion/especialidades/editar/<int:pk>/",
        views.update_especialidad,
        name="update_especialidad",
    ),
    path(
        "gestion/especialidades/eliminar/<int:pk>/",
        views.delete_especialidad,
        name="delete_especialidad",
    ),
]
