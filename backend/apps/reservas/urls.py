from rest_framework.routers import DefaultRouter

from .views import ReservaViewSet

app_name = "reservas"

router = DefaultRouter()
router.register("reservas", ReservaViewSet, basename="reserva")

urlpatterns = router.urls
