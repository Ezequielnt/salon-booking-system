from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import (
    DateTimeRangeField,
    RangeBoundary,
    RangeOperators,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Func, Q, Sum
from django.utils import timezone


class EstadoReserva(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    CONFIRMADA = "confirmada", "Confirmada"
    CANCELADA = "cancelada", "Cancelada"
    COMPLETADA = "completada", "Completada"


# Máquina de estados: qué transiciones se permiten desde cada estado.
TRANSICIONES_VALIDAS: dict[str, set[str]] = {
    EstadoReserva.PENDIENTE: {EstadoReserva.CONFIRMADA, EstadoReserva.CANCELADA},
    EstadoReserva.CONFIRMADA: {EstadoReserva.CANCELADA, EstadoReserva.COMPLETADA},
    EstadoReserva.CANCELADA: set(),
    EstadoReserva.COMPLETADA: set(),
}

# Estados que "ocupan" el espacio: entran en la restricción de no-solapamiento.
ESTADOS_QUE_OCUPAN = (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA)


class TransicionInvalida(Exception):
    """Se intentó una transición de estado no permitida."""


class TsTzRange(Func):
    """tstzrange(inicio, fin, '[)') para la ExclusionConstraint."""

    function = "TSTZRANGE"
    output_field = DateTimeRangeField()


class Reserva(models.Model):
    espacio = models.ForeignKey(
        "salones.Espacio",
        on_delete=models.PROTECT,
        related_name="reservas",
    )
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reservas",
    )

    inicio = models.DateTimeField()
    fin = models.DateTimeField()

    estado = models.CharField(
        max_length=20,
        choices=EstadoReserva.choices,
        default=EstadoReserva.PENDIENTE,
    )
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "reserva"
        verbose_name_plural = "reservas"
        ordering = ["-inicio"]
        indexes = [
            models.Index(fields=["espacio", "inicio"]),
            models.Index(fields=["estado"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(inicio__lt=F("fin")),
                name="reserva_inicio_antes_de_fin",
            ),
            models.CheckConstraint(
                condition=Q(monto_total__gte=0),
                name="reserva_monto_no_negativo",
            ),
            # Dos reservas que ocupan el mismo espacio no pueden solaparse en
            # el tiempo. Se resuelve en la DB, no en el serializer.
            # Requiere la extensión btree_gist (ver migración 0001).
            ExclusionConstraint(
                name="reserva_sin_solapamiento_por_espacio",
                expressions=[
                    ("espacio", RangeOperators.EQUAL),
                    (
                        TsTzRange("inicio", "fin", RangeBoundary()),
                        RangeOperators.OVERLAPS,
                    ),
                ],
                condition=Q(estado__in=["pendiente", "confirmada"]),
            ),
        ]

    def __str__(self) -> str:
        inicio_local = timezone.localtime(self.inicio) if self.inicio else None
        cuando = f"{inicio_local:%d/%m/%Y %H:%M}" if inicio_local else "sin fecha"
        return f"Reserva #{self.pk} · {cuando} ({self.get_estado_display()})"

    def clean(self):
        if self.inicio and self.fin:
            if self.inicio >= self.fin:
                raise ValidationError("El inicio debe ser anterior al fin.")
            if self.espacio_id and not self.espacio.esta_disponible(
                self.inicio, self.fin, excluir_reserva_id=self.pk
            ):
                raise ValidationError(
                    "El espacio no está disponible en ese horario "
                    "(fuera de horario, bloqueado, o ya reservado)."
                )

    # --- Máquina de estados --------------------------------------------
    def transicionar(self, nuevo_estado: str, *, guardar: bool = True) -> None:
        actual = EstadoReserva(self.estado)
        destino = EstadoReserva(nuevo_estado)
        if destino not in TRANSICIONES_VALIDAS[actual]:
            raise TransicionInvalida(
                f"No se puede pasar de «{actual.label}» a «{destino.label}»."
            )
        self.estado = destino
        if guardar:
            self.save(update_fields=["estado", "actualizado_en"])

        from .signals import reserva_transicionada

        reserva_transicionada.send(
            sender=type(self), reserva=self, anterior=actual, nuevo=destino
        )

    # --- Reglas de negocio ------------------------------------------
    @property
    def puede_cancelarse(self) -> bool:
        """True si todavía está dentro de la ventana de cancelación del salón."""
        if EstadoReserva(self.estado) not in ESTADOS_QUE_OCUPAN:
            return False
        margen = timedelta(hours=self.espacio.salon.politica_cancelacion_horas)
        return timezone.now() < (self.inicio - margen)

    @property
    def total_pagado(self) -> Decimal:
        total = self.pagos.filter(estado="aprobado").aggregate(s=Sum("monto"))["s"]
        return total or Decimal("0.00")

    @property
    def saldo_pendiente(self) -> Decimal:
        return self.monto_total - self.total_pagado
