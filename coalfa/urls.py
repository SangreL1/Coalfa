from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("registro/", views.registro_view, name="registro"),
    path("gestion/solicitudes/", views.admin_solicitudes, name="admin_solicitudes"),
    path("gestion/solicitudes/<int:pk>/aprobar/", views.admin_aprobar, name="admin_aprobar"),
    path("gestion/solicitudes/<int:pk>/rechazar/", views.admin_rechazar, name="admin_rechazar"),
]
