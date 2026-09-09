"""Smoke test del checkout fake. Corre con:

    docker compose run --rm backend python scripts/smoke_checkout.py
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

for r in Reserva.objects.filter(notas="smoke-checkout"):
    Pago.objects.filter(reserva=r).delete()
    r.delete()

c = APIClient()


def check(label, cond, extra=""):
    print(f"  {'OK ' if cond else 'FAIL'} {label} {extra}")
    assert cond, label


def login(u, p):
    r = c.post("/api/v1/auth/token/", {"username": u, "password": p}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")


login("cliente", "demo1234")
espacio = Espacio.objects.filter(activo=True).first()
hoy = timezone.localdate()
sabado = hoy + timedelta(days=(5 - hoy.weekday()) % 7 or 7)
r = c.get(f"/api/v1/espacios/{espacio.id}/disponibilidad/?fecha={sabado.isoformat()}")
hueco = next(h for h in r.data["libre"] if datetime.fromisoformat(h["fin"]) - datetime.fromisoformat(h["inicio"]) >= timedelta(hours=2))
inicio = datetime.fromisoformat(hueco["inicio"])

r = c.post("/api/v1/reservas/", {"espacio": espacio.id, "inicio": inicio.isoformat(), "fin": (inicio + timedelta(hours=2)).isoformat(), "notas": "smoke-checkout"}, format="json")
check("reserva creada", r.status_code == 201, r.content)
reserva_id = r.data["id"]

r = c.post("/api/v1/pagos/", {"reserva": reserva_id, "tipo": "sena", "monto": "10000.00"}, format="json")
check("seña creada", r.status_code == 201, r.content)
pago_id = r.data["id"]

# 1. checkout -> URL + token
r = c.post(f"/api/v1/pagos/{pago_id}/checkout/")
check("checkout devuelve url y token", r.status_code == 200 and "checkout_url" in r.data and r.data["token"], r.data)
token = r.data["token"]
check("checkout_url apunta al frontend", r.data["checkout_url"].startswith("http://localhost:5173/checkout/"))

# 2. callback SIN auth (el token es la credencial)
anon = APIClient()
r = anon.post("/api/v1/pagos/checkout/resolver/", {"token": token, "resultado": "aprobado"}, format="json")
check("callback aprueba el pago sin JWT", r.status_code == 200 and r.data["estado"] == "aprobado", r.content)

# 3. la reserva quedó confirmada por la seña
r = c.get(f"/api/v1/reservas/{reserva_id}/")
check("reserva confirmada por el checkout", r.data["estado"] == "confirmada", r.data)

# 4. callback repetido = idempotente
r = anon.post("/api/v1/pagos/checkout/resolver/", {"token": token, "resultado": "aprobado"}, format="json")
check("callback repetido no rompe", r.status_code == 200 and r.data["estado"] == "aprobado")

# 5. token inválido
r = anon.post("/api/v1/pagos/checkout/resolver/", {"token": "basura", "resultado": "aprobado"}, format="json")
check("token inválido -> 400", r.status_code == 400, r.content)

# 6. checkout sobre un pago ya aprobado -> 400
r = c.post(f"/api/v1/pagos/{pago_id}/checkout/")
check("checkout sobre pago no pendiente -> 400", r.status_code == 400, r.content)

Pago.objects.filter(reserva_id=reserva_id).delete()
Reserva.objects.filter(pk=reserva_id).delete()
print("\nSmoke checkout OK")
