from django.db import models


class TipoNotificacion(models.TextChoices):
    CONFIRMACION = "confirmacion", "Confirmación de reserva"
    RECORDATORIO_24H = "recordatorio_24h", "Recordatorio 24 h antes"
    CANCELACION = "cancelacion", "Cancelación de reserva"


class Notificacion(models.Model):
    """Registro de un email disparado por una reserva. Lo consume una
    task de Celery. El unique (reserva, tipo) da idempotencia: el worker
    no manda dos veces el mismo recordatorio."""

    reserva = models.ForeignKey(
        "reservas.Reserva",
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    tipo = models.CharField(max_length=20, choices=TipoNotificacion.choices)
    enviado = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True, help_text="Último error de envío, si lo hubo.")

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "notificación"
        verbose_name_plural = "notificaciones"
        ordering = ["-creado_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["reserva", "tipo"],
                name="notificacion_unica_por_tipo_y_reserva",
            ),
        ]

    def __str__(self) -> str:
        estado = "enviada" if self.enviado else "pendiente"
        return f"{self.get_tipo_display()} · reserva #{self.reserva_id} ({estado})"
