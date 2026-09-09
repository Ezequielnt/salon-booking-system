from rest_framework import viewsets

from apps.core.permissions import SoloLecturaOAdminSalon
from apps.usuarios.models import Rol

from .models import Espacio, Salon
from .serializers import EspacioSerializer, SalonSerializer


class SalonViewSet(viewsets.ModelViewSet):
    """Salones. El cliente ve los activos; el admin_salon gestiona los suyos."""

    queryset = Salon.objects.none()  # el real se arma en get_queryset()
    serializer_class = SalonSerializer
    permission_classes = [SoloLecturaOAdminSalon]
    search_fields = ("nombre", "direccion")
    ordering_fields = ("nombre",)

    def get_queryset(self):
        qs = Salon.objects.prefetch_related("espacios").all()
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_staff:
            return qs
        if user.rol == Rol.ADMIN_SALON:
            return qs.filter(owner=user)
        return qs.filter(activo=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EspacioViewSet(viewsets.ModelViewSet):
    """Espacios reservables. Scoping igual que Salon, vía `salon__owner`."""

    queryset = Espacio.objects.none()  # el real se arma en get_queryset()
    serializer_class = EspacioSerializer
    permission_classes = [SoloLecturaOAdminSalon]
    filterset_fields = ("salon", "activo")
    search_fields = ("nombre",)
    ordering_fields = ("nombre", "capacidad", "precio_base")

    def get_queryset(self):
        qs = Espacio.objects.select_related("salon").all()
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_staff:
            return qs
        if user.rol == Rol.ADMIN_SALON:
            return qs.filter(salon__owner=user)
        return qs.filter(activo=True, salon__activo=True)
