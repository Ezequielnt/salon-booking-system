"""Señales de dominio de Reserva.

`reserva_transicionada` se emite desde `Reserva.transicionar()` cada vez que
una reserva entra a un estado nuevo. La app `notificaciones` la escucha para
disparar los emails, sin que `reservas` tenga que conocer a `notificaciones`.
"""

from django.dispatch import Signal

# kwargs: reserva (Reserva), anterior (EstadoReserva), nuevo (EstadoReserva)
reserva_transicionada = Signal()
