"""Tasks de Celery para notificaciones y mantenimiento de reservas.

- `enviar_notificacion` — manda un email puntual, con reintentos.
- `notificar_reserva` — registra + encola el envío para una reserva.
- `enviar_recordatorios` (beat) — recordatorio 24 h antes de cada reserva confirmada.
- `completar_reservas_vencidas` (beat) — pasa a COMPLETADA las que ya terminaron.
"""

from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from apps.reservas.models import EstadoReserva, Reserva, TransicionInvalida

from . import services
from .models import Notificacion, TipoNotificacion

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def enviar_notificacion(self, notificacion_id: int) -> None:
    notificacion = (
        Notificacion.objects.select_related(
            "reserva", "reserva__cliente", "reserva__espacio__salon"
        )
        .filter(pk=notificacion_id)
        .first()
    )
    if notificacion is None:
        logger.warning("Notificación %s ya no existe", notificacion_id)
        return
    services.enviar(notificacion)


@shared_task
def notificar_reserva(reserva_id: int, tipo: str) -> None:
    """Registra la notificación de `tipo` para la reserva y encola su envío."""
    reserva = Reserva.objects.filter(pk=reserva_id).first()
    if reserva is None:
        return
    notificacion, _ = services.registrar(reserva, tipo)
    if not notificacion.enviado:
        enviar_notificacion.delay(notificacion.pk)


@shared_task
def enviar_recordatorios() -> int:
    """Reservas confirmadas que arrancan dentro de las próximas 24 h y todavía
    no recibieron el recordatorio. Devuelve cuántas encoló."""
    ahora = timezone.now()
    proximas = (
        Reserva.objects.filter(
            estado=EstadoReserva.CONFIRMADA,
            inicio__gt=ahora,
            inicio__lte=ahora + timedelta(hours=24),
        )
        .exclude(notificaciones__tipo=TipoNotificacion.RECORDATORIO_24H)
    )
    encoladas = 0
    for reserva in proximas:
        notificar_reserva.delay(reserva.pk, TipoNotificacion.RECORDATORIO_24H)
        encoladas += 1
    logger.info("Recordatorios encolados: %s", encoladas)
    return encoladas


@shared_task
def completar_reservas_vencidas() -> int:
    """Pasa a COMPLETADA las reservas confirmadas cuyo evento ya terminó."""
    ahora = timezone.now()
    vencidas = Reserva.objects.filter(estado=EstadoReserva.CONFIRMADA, fin__lt=ahora)
    completadas = 0
    for reserva in vencidas:
        try:
            reserva.transicionar(EstadoReserva.COMPLETADA)
            completadas += 1
        except TransicionInvalida:
            pass
    logger.info("Reservas completadas: %s", completadas)
    return completadas
