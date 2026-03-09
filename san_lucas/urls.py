"""
Root URL configuration for Coalfa system.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Administración Coalfa"
admin.site.site_title = "Coalfa"
admin.site.index_title = "Panel de Administración"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("coalfa.urls")),
    path("rrhh/", include("rrhh.urls")),
    path("inventario/", include("inventario.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)