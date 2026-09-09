from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.usuarios.models import Rol

from .models import EstadoPago, Pago, TransicionInvalida
from .serializers import PagoSerializer


class PagoViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Pagos de una reserva (seña / saldo).

    No se editan ni borran: un pago avanza por su máquina de estados con las
    acciones `aprobar` / `rechazar` / `reembolsar`, que simulan el webhook del
    proveedor (en la demo el proveedor es "fake").
    """

    queryset = Pago.objects.none()  # el real se arma en get_queryset()
    serializer_class = PagoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ("reserva", "tipo", "estado")
    ordering = ("-creado_en",)

    def get_queryset(self):
        qs = Pago.objects.select_related("reserva", "reserva__espacio__salon", "reserva__cliente")
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_staff:
            return qs
        if user.rol == Rol.ADMIN_SALON:
            return qs.filter(reserva__espacio__salon__owner=user)
        return qs.filter(reserva__cliente=user)

    def _es_gestor(self, pago):
        user = self.request.user
        return user.is_staff or pago.reserva.espacio.salon.owner_id == user.id

    def _transicionar(self, nuevo_estado):
        pago = self.get_object()
        if not self._es_gestor(pago):
            raise PermissionDenied("Solo el salón registra el resultado de un pago.")
        try:
            pago.transicionar(nuevo_estado)
        except TransicionInvalida as exc:
            raise ValidationError(str(exc))
        return Response(self.get_serializer(pago).data)

    @extend_schema(request=None, responses=PagoSerializer)
    @action(detail=True, methods=["post"])
    def aprobar(self, request, pk=None):
        """Simula la aprobación del proveedor. Si es la seña, confirma la reserva."""
        return self._transicionar(EstadoPago.APROBADO)

    @extend_schema(request=None, responses=PagoSerializer)
    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        return self._transicionar(EstadoPago.RECHAZADO)

    @extend_schema(request=None, responses=PagoSerializer)
    @action(detail=True, methods=["post"])
    def reembolsar(self, request, pk=None):
        return self._transicionar(EstadoPago.REEMBOLSADO)
