"""Carga un set mínimo de datos para poder probar la demo.

Idempotente: se puede correr varias veces sin duplicar nada.
Lo ejecuta el entrypoint del contenedor `backend` al arrancar.
"""

from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.disponibilidad.models import BloqueoFecha, DiaSemana, ReglaDisponibilidad
from apps.pagos.models import EstadoPago, Pago, TipoPago
from apps.reservas.models import EstadoReserva, Reserva
from apps.salones.models import Espacio, Salon
from apps.usuarios.models import Rol

User = get_user_model()


class Command(BaseCommand):
    help = "Carga datos de demo (usuarios, un salón con espacios, disponibilidad y una reserva)."

    @transaction.atomic
    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@salon.local",
                "rol": Rol.STAFF,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        _set_password(admin, "admin")

        dueno, _ = User.objects.get_or_create(
            username="dueno",
            defaults={"email": "dueno@salon.local", "rol": Rol.ADMIN_SALON},
        )
        _set_password(dueno, "demo1234")

        cliente, _ = User.objects.get_or_create(
            username="cliente",
            defaults={"email": "cliente@salon.local", "rol": Rol.CLIENTE},
        )
        _set_password(cliente, "demo1234")

        salon, _ = Salon.objects.get_or_create(
            nombre="Salón Belgrano",
            defaults={
                "owner": dueno,
                "direccion": "Av. Cabildo 2000, CABA",
                "descripcion": "Salón de eventos con tres espacios independientes.",
                "politica_cancelacion_horas": 48,
            },
        )

        espacios = {}
        for nombre, capacidad, precio in [
            ("Salón Principal", 200, "150000.00"),
            ("Jardín", 120, "90000.00"),
            ("Terraza", 60, "50000.00"),
        ]:
            espacios[nombre], _ = Espacio.objects.get_or_create(
                salon=salon,
                nombre=nombre,
                defaults={"capacidad": capacidad, "precio_base": Decimal(precio)},
            )

        # Disponibilidad: viernes, sábado y domingo de 10:00 a 23:00.
        for espacio in espacios.values():
            for dia in (DiaSemana.VIERNES, DiaSemana.SABADO, DiaSemana.DOMINGO):
                ReglaDisponibilidad.objects.get_or_create(
                    espacio=espacio,
                    dia_semana=dia,
                    hora_inicio=time(10, 0),
                    hora_fin=time(23, 0),
                )

        # Bloqueo de ejemplo: Jardín en mantenimiento el próximo lunes.
        lunes = _proximo_dia_semana(0).replace(hour=8)
        BloqueoFecha.objects.get_or_create(
            espacio=espacios["Jardín"],
            inicio=lunes,
            fin=lunes + timedelta(hours=10),
            defaults={"motivo": "Mantenimiento de riego"},
        )

        # Reserva de ejemplo: cliente en Salón Principal, próximo sábado 20–23 h.
        sabado = _proximo_dia_semana(5).replace(hour=20)
        reserva, creada = Reserva.objects.get_or_create(
            espacio=espacios["Salón Principal"],
            inicio=sabado,
            defaults={
                "cliente": cliente,
                "fin": sabado + timedelta(hours=3),
                "monto_total": Decimal("150000.00"),
                "notas": "Cumpleaños, 50 personas.",
            },
        )
        if creada:
            Pago.objects.create(
                reserva=reserva,
                tipo=TipoPago.SENA,
                monto=Decimal("45000.00"),
                estado=EstadoPago.APROBADO,
                proveedor="fake",
                referencia_externa="demo-sena-0001",
            )
            reserva.transicionar(EstadoReserva.CONFIRMADA)

        self.stdout.write(self.style.SUCCESS("Datos de demo cargados:"))
        self.stdout.write("  admin de Django : admin / admin")
        self.stdout.write("  dueño de salón  : dueno / demo1234")
        self.stdout.write("  cliente         : cliente / demo1234")


def _set_password(user, raw_password: str) -> None:
    """Fija la contraseña solo si el usuario no tiene una (primera corrida)."""
    if not user.has_usable_password():
        user.set_password(raw_password)
        user.save(update_fields=["password"])


def _proximo_dia_semana(weekday: int):
    """Próxima fecha futura que cae en `weekday` (0=lunes … 6=domingo)."""
    ahora = timezone.localtime()
    delta = (weekday - ahora.weekday()) % 7 or 7
    return (ahora + timedelta(days=delta)).replace(
        minute=0, second=0, microsecond=0
    )
