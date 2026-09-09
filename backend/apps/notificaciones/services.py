"""Composición y envío de las notificaciones por email.

Separado de `tasks.py` para poder testear el contenido sin Celery. Cada
`Notificacion` es idempotente: el UniqueConstraint (reserva, tipo) impide
duplicados y `enviar()` no re-manda una ya enviada.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Notificacion, TipoNotificacion

ASUNTOS = {
    TipoNotificacion.CONFIRMACION: "Reserva confirmada — {salon}",
    TipoNotificacion.RECORDATORIO_24H: "Recordatorio: tu reserva en {salon} es mañana",
    TipoNotificacion.CANCELACION: "Reserva cancelada — {salon}",
}


def registrar(reserva, tipo) -> tuple[Notificacion, bool]:
    """Crea (o recupera) la notificación de ese tipo para la reserva."""
    return Notificacion.objects.get_or_create(reserva=reserva, tipo=tipo)


def _contexto(reserva) -> dict:
    return {
        "cliente": reserva.cliente.get_full_name() or reserva.cliente.username,
        "salon": reserva.espacio.salon.nombre,
        "espacio": reserva.espacio.nombre,
        "inicio": timezone.localtime(reserva.inicio),
        "fin": timezone.localtime(reserva.fin),
        "monto_total": reserva.monto_total,
        "total_pagado": reserva.total_pagado,
        "saldo_pendiente": reserva.saldo_pendiente,
    }


def componer(notificacion: Notificacion) -> tuple[str, str, str]:
    """Devuelve (asunto, cuerpo, destinatario) para esa notificación."""
    reserva = notificacion.reserva
    ctx = _contexto(reserva)
    asunto = ASUNTOS[notificacion.tipo].format(salon=ctx["salon"])
    cuerpo = render_to_string(f"notificaciones/{notificacion.tipo}.txt", ctx)
    return asunto, cuerpo, reserva.cliente.email


def enviar(notificacion: Notificacion) -> bool:
    """Manda el email. Marca `enviado` o guarda el `error`. Devuelve si se envió."""
    if notificacion.enviado:
        return True
    asunto, cuerpo, destinatario = componer(notificacion)
    if not destinatario:
        notificacion.error = "El cliente no tiene email cargado."
        notificacion.save(update_fields=["error"])
        return False
    try:
        send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, [destinatario])
    except Exception as exc:  # noqa: BLE001 — se registra y se deja reintentar
        notificacion.error = str(exc)
        notificacion.save(update_fields=["error"])
        raise
    notificacion.enviado = True
    notificacion.fecha_envio = timezone.now()
    notificacion.error = ""
    notificacion.save(update_fields=["enviado", "fecha_envio", "error"])
    return True
