from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.usuarios.models import Rol

from .models import EstadoReserva, Reserva, TransicionInvalida
from .serializers import ReservaSerializer


class ReservaViewSet(viewsets.ModelViewSet):
    """Reservas.

    - cliente: ve y crea las suyas; puede cancelarlas dentro de la ventana.
    - admin_salon: ve y gestiona las de sus espacios (confirmar/cancelar/completar).
    - staff: todo.
    """

    queryset = Reserva.objects.none()  # el real se arma en get_queryset()
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ("estado", "espacio", "espacio__salon")
    ordering_fields = ("inicio", "creado_en")
    ordering = ("-inicio",)

    def get_queryset(self):
        qs = Reserva.objects.select_related("espacio", "espacio__salon", "cliente").prefetch_related("pagos")
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_staff:
            return qs
        if user.rol == Rol.ADMIN_SALON:
            return qs.filter(espacio__salon__owner=user)
        return qs.filter(cliente=user)

    # --- Transiciones de estado -------------------------------------------

    def _es_gestor(self, reserva):
        """El que llama puede gestionar (confirmar/completar) esta reserva."""
        user = self.request.user
        return user.is_staff or reserva.espacio.salon.owner_id == user.id

    def _transicionar(self, request, nuevo_estado):
        reserva = self.get_object()
        try:
            reserva.transicionar(nuevo_estado)
        except TransicionInvalida as exc:
            raise ValidationError(str(exc))
        return Response(self.get_serializer(reserva).data)

    @extend_schema(request=None, responses=ReservaSerializer)
    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):
        """Confirma la reserva sin pago (uso del admin_salon)."""
        if not self._es_gestor(self.get_object()):
            raise PermissionDenied("Solo el salón puede confirmar la reserva.")
        return self._transicionar(request, EstadoReserva.CONFIRMADA)

    @extend_schema(request=None, responses=ReservaSerializer)
    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """Cancela la reserva. El cliente solo dentro de la ventana de cancelación."""
        reserva = self.get_object()
        if not self._es_gestor(reserva) and not reserva.puede_cancelarse:
            raise PermissionDenied(
                "Pasó la ventana de cancelación. Contactá al salón."
            )
        return self._transicionar(request, EstadoReserva.CANCELADA)

    @extend_schema(request=None, responses=ReservaSerializer)
    @action(detail=True, methods=["post"])
    def completar(self, request, pk=None):
        """Marca la reserva como completada (uso del admin_salon / tarea Celery)."""
        if not self._es_gestor(self.get_object()):
            raise PermissionDenied("Solo el salón puede completar la reserva.")
        return self._transicionar(request, EstadoReserva.COMPLETADA)
