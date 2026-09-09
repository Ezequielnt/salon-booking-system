"""Cálculo de disponibilidad de un espacio.

Fuente de verdad para "¿cuándo se puede reservar este espacio?". Combina:

1. `ReglaDisponibilidad` — franjas horarias recurrentes en que el espacio abre.
2. `BloqueoFecha` — rangos puntuales en que NO se puede reservar (pisan las reglas).
3. `Reserva` en estado que ocupa (pendiente / confirmada).

`Espacio.esta_disponible()` responde sí/no para un rango concreto; estas
funciones devuelven la grilla del día para que el frontend la pinte.
"""

from datetime import datetime, timedelta

from django.utils import timezone

from apps.reservas.models import ESTADOS_QUE_OCUPAN

from .models import DiaSemana


def _combinar(fecha, hora):
    """Devuelve un datetime tz-aware en la zona local a partir de date + time."""
    return timezone.make_aware(datetime.combine(fecha, hora))


def _restar_intervalos(libres, ocupados):
    """Resta la lista `ocupados` de la lista `libres` (ambas de tuplas (inicio, fin))."""
    resultado = []
    for inicio, fin in libres:
        trozos = [(inicio, fin)]
        for ocup_ini, ocup_fin in ocupados:
            nuevos = []
            for t_ini, t_fin in trozos:
                if ocup_fin <= t_ini or ocup_ini >= t_fin:
                    nuevos.append((t_ini, t_fin))
                    continue
                if ocup_ini > t_ini:
                    nuevos.append((t_ini, ocup_ini))
                if ocup_fin < t_fin:
                    nuevos.append((ocup_fin, t_fin))
            trozos = nuevos
        resultado.extend(trozos)
    return resultado


def franjas_del_dia(espacio, fecha):
    """Franjas (inicio, fin) tz-aware en que el espacio abre ese día, según reglas."""
    reglas = espacio.reglas_disponibilidad.filter(dia_semana=fecha.weekday())
    return [
        (_combinar(fecha, r.hora_inicio), _combinar(fecha, r.hora_fin))
        for r in reglas.order_by("hora_inicio")
    ]


def ocupacion(espacio, desde, hasta):
    """Intervalos ocupados (reservas activas + bloqueos) que solapan [desde, hasta]."""
    eventos = []
    reservas = espacio.reservas.filter(
        estado__in=ESTADOS_QUE_OCUPAN, inicio__lt=hasta, fin__gt=desde
    )
    for r in reservas:
        eventos.append(
            {"inicio": r.inicio, "fin": r.fin, "tipo": "reserva", "detalle": f"Reserva #{r.pk}"}
        )
    bloqueos = espacio.bloqueos.filter(inicio__lt=hasta, fin__gt=desde)
    for b in bloqueos:
        eventos.append(
            {"inicio": b.inicio, "fin": b.fin, "tipo": "bloqueo", "detalle": b.motivo or "Bloqueado"}
        )
    return sorted(eventos, key=lambda e: e["inicio"])


def disponibilidad_del_dia(espacio, fecha):
    """Resumen del día: si abre, sus franjas, lo ocupado y los huecos libres."""
    franjas = franjas_del_dia(espacio, fecha)
    if not franjas:
        return {
            "fecha": fecha,
            "abierto": False,
            "franjas": [],
            "ocupado": [],
            "libre": [],
        }

    inicio_dia = min(f[0] for f in franjas)
    fin_dia = max(f[1] for f in franjas)
    eventos = ocupacion(espacio, inicio_dia, fin_dia)
    ocupados = [(e["inicio"], e["fin"]) for e in eventos]
    libre = _restar_intervalos(franjas, ocupados)

    return {
        "fecha": fecha,
        "abierto": True,
        "dia_semana": DiaSemana(fecha.weekday()).label,
        "franjas": [{"inicio": i, "fin": f} for i, f in franjas],
        "ocupado": eventos,
        "libre": [{"inicio": i, "fin": f} for i, f in libre],
    }
