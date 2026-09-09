from datetime import date, datetime, time

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.salones.models import Espacio
from apps.usuarios.models import Rol

from . import services
from .models import BloqueoFecha, ReglaDisponibilidad
from .serializers import (
    BloqueoFechaSerializer,
    DisponibilidadDiaSerializer,
    EventoOcupacionSerializer,
    ReglaDisponibilidadSerializer,
)


class _AdminSalonScopedViewSet(viewsets.ModelViewSet):
    """Base: solo el admin_salon dueño del espacio (o staff) ve/edita el recurso."""

    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ("espacio",)

    def get_queryset(self):
        qs = self.model.objects.select_related("espacio", "espacio__salon")
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_staff:
            return qs
        if user.rol == Rol.ADMIN_SALON:
            return qs.filter(espacio__salon__owner=user)
        return qs.none()


class ReglaDisponibilidadViewSet(_AdminSalonScopedViewSet):
    model = ReglaDisponibilidad
    queryset = ReglaDisponibilidad.objects.none()  # el real se arma en get_queryset()
    serializer_class = ReglaDisponibilidadSerializer


class BloqueoFechaViewSet(_AdminSalonScopedViewSet):
    model = BloqueoFecha
    queryset = BloqueoFecha.objects.none()  # el real se arma en get_queryset()
    serializer_class = BloqueoFechaSerializer


def _espacio_visible(user, espacio_id):
    """El espacio que el usuario puede consultar, o 404."""
    qs = Espacio.objects.select_related("salon")
    if not user.is_staff:
        if user.rol == Rol.ADMIN_SALON:
            qs = qs.filter(salon__owner=user)
        else:
            qs = qs.filter(activo=True, salon__activo=True)
    return get_object_or_404(qs, pk=espacio_id)


def _parse_fecha(valor):
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise ValidationError(f"Fecha inválida: «{valor}». Usá YYYY-MM-DD.")


class DisponibilidadEspacioView(APIView):
    """GET /api/v1/espacios/{id}/disponibilidad/?fecha=YYYY-MM-DD

    Grilla del día: franjas abiertas (reglas), ocupación y huecos libres.
    Alimenta el formulario de reserva."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter("fecha", str, description="YYYY-MM-DD (default: hoy)")],
        responses=DisponibilidadDiaSerializer,
    )
    def get(self, request, espacio_id):
        espacio = _espacio_visible(request.user, espacio_id)
        fecha = _parse_fecha(request.query_params.get("fecha")) or timezone.localdate()
        data = services.disponibilidad_del_dia(espacio, fecha)
        return Response(DisponibilidadDiaSerializer(data).data)


class OcupacionEspacioView(APIView):
    """GET /api/v1/espacios/{id}/ocupacion/?desde=&hasta=

    Eventos ocupados (reservas activas + bloqueos) en el rango. Formato pensado
    para pintarlos en FullCalendar."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("desde", str, description="YYYY-MM-DD (requerido)"),
            OpenApiParameter("hasta", str, description="YYYY-MM-DD (requerido)"),
        ],
        responses=EventoOcupacionSerializer(many=True),
    )
    def get(self, request, espacio_id):
        espacio = _espacio_visible(request.user, espacio_id)
        desde = _parse_fecha(request.query_params.get("desde"))
        hasta = _parse_fecha(request.query_params.get("hasta"))
        if not (desde and hasta):
            raise ValidationError("Parámetros `desde` y `hasta` (YYYY-MM-DD) son obligatorios.")
        desde_dt = timezone.make_aware(datetime.combine(desde, time.min))
        hasta_dt = timezone.make_aware(datetime.combine(hasta, time.max))
        eventos = services.ocupacion(espacio, desde_dt, hasta_dt)
        return Response(EventoOcupacionSerializer(eventos, many=True).data)
