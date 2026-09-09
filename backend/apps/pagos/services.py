"""Checkout "fake" de pagos.

No hay pasarela real: `crear_checkout` devuelve una URL a una pantalla del
frontend que simula el pago, y `resolver_checkout` es el "callback" que esa
pantalla dispara (equivale al webhook que mandaría Mercado Pago / Stripe).

El token es un `signing.dumps` firmado con `SECRET_KEY` y con vencimiento:
hace de credencial del callback, igual que la firma de un webhook real.
"""

from django.conf import settings
from django.core import signing

from .models import EstadoPago, Pago, TransicionInvalida

_SALT = "pagos.checkout"

RESULTADOS = {
    "aprobado": EstadoPago.APROBADO,
    "rechazado": EstadoPago.RECHAZADO,
}


class CheckoutInvalido(Exception):
    """Token de checkout inválido, vencido o pago en estado incompatible."""


def crear_checkout(pago: Pago) -> dict:
    if pago.estado != EstadoPago.PENDIENTE:
        raise CheckoutInvalido("El pago ya no está pendiente.")
    token = signing.dumps({"pago": pago.pk}, salt=_SALT)
    return {
        "checkout_url": f"{settings.FRONTEND_URL}/checkout/{token}",
        "token": token,
        "monto": pago.monto,
    }


def resolver_checkout(token: str, resultado: str) -> Pago:
    """Aplica el resultado del checkout al pago. Idempotente por token."""
    nuevo_estado = RESULTADOS.get(resultado)
    if nuevo_estado is None:
        raise CheckoutInvalido(f"Resultado desconocido: «{resultado}».")
    try:
        data = signing.loads(token, salt=_SALT, max_age=settings.PAYMENTS_CHECKOUT_TTL)
    except signing.SignatureExpired as exc:
        raise CheckoutInvalido("El link de pago venció.") from exc
    except signing.BadSignature as exc:
        raise CheckoutInvalido("Link de pago inválido.") from exc

    pago = Pago.objects.select_related("reserva").filter(pk=data["pago"]).first()
    if pago is None:
        raise CheckoutInvalido("El pago ya no existe.")
    if pago.estado == nuevo_estado:
        return pago  # callback repetido: no hacemos nada
    try:
        pago.transicionar(nuevo_estado)
    except TransicionInvalida as exc:
        raise CheckoutInvalido(str(exc)) from exc
    return pago
