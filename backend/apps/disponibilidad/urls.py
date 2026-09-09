from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    BloqueoFechaViewSet,
    DisponibilidadEspacioView,
    OcupacionEspacioView,
    ReglaDisponibilidadViewSet,
)

app_name = "disponibilidad"

router = DefaultRouter()
router.register("reglas-disponibilidad", ReglaDisponibilidadViewSet, basename="regla")
router.register("bloqueos", BloqueoFechaViewSet, basename="bloqueo")

urlpatterns = router.urls + [
    path(
        "espacios/<int:espacio_id>/disponibilidad/",
        DisponibilidadEspacioView.as_view(),
        name="espacio-disponibilidad",
    ),
    path(
        "espacios/<int:espacio_id>/ocupacion/",
        OcupacionEspacioView.as_view(),
        name="espacio-ocupacion",
    ),
]
