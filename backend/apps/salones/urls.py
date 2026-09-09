from rest_framework.routers import DefaultRouter

from .views import EspacioViewSet, SalonViewSet

app_name = "salones"

router = DefaultRouter()
router.register("salones", SalonViewSet, basename="salon")
router.register("espacios", EspacioViewSet, basename="espacio")

urlpatterns = router.urls
