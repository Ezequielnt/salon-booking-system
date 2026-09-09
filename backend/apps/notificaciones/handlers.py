"""Conecta las transiciones de Reserva con el envío de notificaciones.

Se registra desde `NotificacionesConfig.ready()`. Usa `transaction.on_commit`
para encolar la task recién cuando la transacción confirmó: si no, el worker
podría tomar la task antes de que la fila sea visible.
"""

from django.db import transaction
from django.dispatch import receiver

from apps.reservas.models import EstadoReserva
from apps.reservas.signals import reserva_transicionada

from . import tasks
from .models import TipoNotificacion

_TIPO_POR_ESTADO = {
    EstadoReserva.CONFIRMADA: TipoNotificacion.CONFIRMACION,
    EstadoReserva.CANCELADA: TipoNotificacion.CANCELACION,
}


@receiver(reserva_transicionada, dispatch_uid="notificaciones.notificar_transicion")
def notificar_transicion(sender, reserva, anterior, nuevo, **kwargs):
    tipo = _TIPO_POR_ESTADO.get(nuevo)
    if tipo is None:
        return
    transaction.on_commit(
        lambda: tasks.notificar_reserva.delay(reserva.pk, tipo)
    )
