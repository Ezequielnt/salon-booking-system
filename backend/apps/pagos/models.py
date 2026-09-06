from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class TipoPago(models.TextChoices):
    SENA = "sena", "Seña"
    SALDO = "saldo", "Saldo"


class EstadoPago(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    APROBADO = "aprobado", "Aprobado"
    RECHAZADO = "rechazado", "Rechazado"
    REEMBOLSADO = "reembolsado", "Reembolsado"


class Pago(models.Model):
    """Un pago asociado a una reserva. Una reserva puede tener una seña
    y un saldo. La reserva pasa a CONFIRMADA cuando la seña queda APROBADA."""

    reserva = models.ForeignKey(
        "reservas.Reserva",
        on_delete=models.PROTECT,
        related_name="pagos",
    )
    tipo = models.CharField(max_length=10, choices=TipoPago.choices)
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE,
    )
    proveedor = models.CharField(
        max_length=30,
        default="fake",
        help_text='"fake" para la demo, "mercadopago" en modo real.',
    )
    referencia_externa = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID de la transacción en el proveedor de pagos.",
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "pago"
        verbose_name_plural = "pagos"
        ordering = ["-creado_en"]
        constraints = [
            # Como máximo un pago "vivo" (pendiente o aprobado) por tipo y
            # reserva. Los rechazados no cuentan: permiten reintentar.
            models.UniqueConstraint(
                fields=["reserva", "tipo"],
                condition=Q(estado__in=["pendiente", "aprobado"]),
                name="pago_activo_unico_por_tipo_y_reserva",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} ${self.monto} · reserva #{self.reserva_id} ({self.get_estado_display()})"
