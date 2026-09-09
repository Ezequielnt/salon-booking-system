"""Smoke test de notificaciones + tasks de mantenimiento. Corre con:

    docker compose run --rm -e CELERY_TASK_ALWAYS_EAGER=1 backend python scripts/smoke_notificaciones.py

Con EAGER las tasks corren sincrónicas, así que se puede verificar el efecto
sin levantar el worker.
"""

import os
import sys
from pathlib import Path

import django

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from datetime import timedelta  # noqa: E402
from decimal import Decimal  # noqa: E402

from django.core import mail  # noqa: E402
from django.test.utils import override_settings  # noqa: E402
from django.utils import timezone  # noqa: E402

from apps.notificaciones.models import Notificacion, TipoNotificacion  # noqa: E402
from apps.notificaciones.tasks import (  # noqa: E402
    completar_reservas_vencidas,
    enviar_recordatorios,
)
from apps.pagos.models import EstadoPago, Pago, TipoPago  # noqa: E402
from apps.reservas.models import EstadoReserva, Reserva  # noqa: E402
from apps.salones.models import Espacio  # noqa: E402


def check(label, cond, extra=""):
    print(f"  {'OK ' if cond else 'FAIL'} {label} {extra}")
    assert cond, label


# Limpieza previa
Notificacion.objects.filter(reserva__notas="smoke-notif").delete()
Pago.objects.filter(reserva__notas="smoke-notif").delete()
Reserva.objects.filter(notas="smoke-notif").delete()

espacio = Espacio.objects.filter(activo=True).first()
cliente = espacio.salon.owner.__class__.objects.get(username="cliente")

# Reserva mañana, dentro de la ventana de recordatorio.
inicio = timezone.now() + timedelta(hours=12)
reserva = Reserva.objects.create(
    espacio=espacio,
    cliente=cliente,
    inicio=inicio,
    fin=inicio + timedelta(hours=3),
    monto_total=espacio.precio_base,
    notas="smoke-notif",
)

with override_settings(
    CELERY_TASK_ALWAYS_EAGER=True, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
):
    mail.outbox = []

    # 1. Confirmar la reserva -> email de confirmación
    pago = Pago.objects.create(
        reserva=reserva, tipo=TipoPago.SENA, monto=Decimal("10000.00"), proveedor="fake"
    )
    pago.transicionar(EstadoPago.APROBADO)  # cascada: reserva -> CONFIRMADA -> señal

    reserva.refresh_from_db()
    check("reserva confirmada por la seña", reserva.estado == EstadoReserva.CONFIRMADA)
    check("email de confirmación enviado", len(mail.outbox) == 1, [m.subject for m in mail.outbox])
    check(
        "notificación de confirmación registrada y marcada",
        Notificacion.objects.get(
            reserva=reserva, tipo=TipoNotificacion.CONFIRMACION
        ).enviado,
    )

    # 2. Beat: recordatorio 24 h
    mail.outbox = []
    n = enviar_recordatorios()
    check("recordatorio encolado para la reserva", n >= 1)
    check("email de recordatorio enviado", any("Recordatorio" in m.subject for m in mail.outbox))
    # idempotente: segunda corrida no re-manda
    mail.outbox = []
    enviar_recordatorios()
    check("recordatorio no se repite", len(mail.outbox) == 0)

    # 3. Beat: completar vencidas
    Reserva.objects.filter(pk=reserva.pk).update(
        inicio=timezone.now() - timedelta(hours=5), fin=timezone.now() - timedelta(hours=2)
    )
    completadas = completar_reservas_vencidas()
    reserva.refresh_from_db()
    check("reserva vencida pasa a completada", reserva.estado == EstadoReserva.COMPLETADA, completadas)

    # 4. Cancelación -> email
    otra_inicio = timezone.now() + timedelta(days=10)
    otra = Reserva.objects.create(
        espacio=espacio, cliente=cliente, inicio=otra_inicio,
        fin=otra_inicio + timedelta(hours=3), monto_total=espacio.precio_base, notas="smoke-notif",
    )
    otra.transicionar(EstadoReserva.CONFIRMADA)
    mail.outbox = []
    otra.transicionar(EstadoReserva.CANCELADA)
    check("email de cancelación enviado", any("cancelada" in m.subject.lower() for m in mail.outbox))

# Limpieza
Notificacion.objects.filter(reserva__notas="smoke-notif").delete()
Pago.objects.filter(reserva__notas="smoke-notif").delete()
Reserva.objects.filter(notas="smoke-notif").delete()
print("\nSmoke notificaciones OK")
