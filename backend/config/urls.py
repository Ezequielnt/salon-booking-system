from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_v1 = [
    path("auth/", include("apps.usuarios.urls")),
    path("", include("apps.salones.urls")),
    path("", include("apps.disponibilidad.urls")),
    path("", include("apps.reservas.urls")),
    path("", include("apps.pagos.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    # Documentación de la API
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/v1/", include(api_v1)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
