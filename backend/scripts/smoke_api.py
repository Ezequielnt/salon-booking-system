"""Smoke test manual de la API. Corre con:

    docker compose run --rm backend python scripts/smoke_api.py

Ejercita el flujo cliente: login -> ver espacios -> disponibilidad -> reservar
-> pagar seña -> la reserva queda confirmada. No es un reemplazo de los tests.
"""

import os
import sys
from pathlib import Path

import django

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from datetime import datetime, timedelta  # noqa: E402

from django.utils import timezone  # noqa: E402
from rest_framework.test import APIClient  # noqa: E402

from apps.pagos.models import Pago  # noqa: E402
from apps.reservas.models import Reserva  # noqa: E402
from apps.salones.models import Espacio  # noqa: E402

# Limpieza de corridas previas (el script deja "smoke" en notas).
for r in Reserva.objects.filter(notas="smoke"):
    Pago.objects.filter(reserva=r).delete()
    r.delete()

c = APIClient()


def login(username, password):
    r = c.post("/api/v1/auth/token/", {"username": username, "password": password}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")


def check(label, cond, extra=""):
    print(f"  {'OK ' if cond else 'FAIL'} {label} {extra}")
    assert cond, label


print("== cliente ==")
login("cliente", "demo1234")

r = c.get("/api/v1/espacios/")
check("lista espacios activos", r.status_code == 200 and r.data["count"] >= 1)
espacio_id = r.data["results"][0]["id"]

# Próximo sábado (el seed abre viernes/sábado/domingo 10-23).
espacio = Espacio.objects.get(pk=espacio_id)
hoy = timezone.localdate()
sabado = hoy + timedelta(days=(5 - hoy.weekday()) % 7 or 7)

r = c.get(f"/api/v1/espacios/{espacio_id}/disponibilidad/?fecha={sabado.isoformat()}")
check("disponibilidad del día", r.status_code == 200 and r.data["abierto"], r.data)

# Tomar el primer hueco libre de al menos 3 h.
hueco = next(h for h in r.data["libre"] if datetime.fromisoformat(h["fin"]) - datetime.fromisoformat(h["inicio"]) >= timedelta(hours=3))
inicio = datetime.fromisoformat(hueco["inicio"])
fin = inicio + timedelta(hours=3)
r = c.post(
    "/api/v1/reservas/",
    {"espacio": espacio_id, "inicio": inicio.isoformat(), "fin": fin.isoformat(), "notas": "smoke"},
    format="json",
)
check("crear reserva", r.status_code == 201, r.content)
reserva_id = r.data["id"]
check("reserva arranca pendiente", r.data["estado"] == "pendiente")
check("monto = precio_base", str(r.data["monto_total"]) == str(espacio.precio_base))

# Solapada -> debe fallar
r = c.post(
    "/api/v1/reservas/",
    {"espacio": espacio_id, "inicio": inicio.isoformat(), "fin": fin.isoformat()},
    format="json",
)
check("reserva solapada rechazada", r.status_code == 400, r.content)

# Pagar seña
r = c.post("/api/v1/pagos/", {"reserva": reserva_id, "tipo": "sena", "monto": "10000.00"}, format="json")
check("crear seña", r.status_code == 201, r.content)
pago_id = r.data["id"]

print("== dueño de salón ==")
login("dueno", "demo1234")
r = c.post(f"/api/v1/pagos/{pago_id}/aprobar/")
check("aprobar seña", r.status_code == 200, r.content)

r = c.get(f"/api/v1/reservas/{reserva_id}/")
check("reserva confirmada por la seña", r.data["estado"] == "confirmada", r.data)

# El dueño ve la reserva de su espacio
r = c.get("/api/v1/reservas/")
check("dueño ve reservas de su salón", any(x["id"] == reserva_id for x in r.data["results"]))

print("== aislamiento ==")
r = c.get("/api/v1/reglas-disponibilidad/")
check("dueño ve sus reglas", r.status_code == 200 and r.data["count"] >= 1)

login("cliente", "demo1234")
r = c.get("/api/v1/reglas-disponibilidad/")
check("cliente no ve reglas (vacío)", r.status_code == 200 and r.data["count"] == 0)

# Limpieza (Pago es PROTECT: primero los pagos)
Pago.objects.filter(reserva_id=reserva_id).delete()
Reserva.objects.filter(pk=reserva_id).delete()
print("\nSmoke OK")
