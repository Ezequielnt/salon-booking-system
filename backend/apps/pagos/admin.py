from django.contrib import admin

from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "reserva", "tipo", "monto", "estado", "proveedor", "creado_en")
    list_filter = ("tipo", "estado", "proveedor")
    search_fields = ("reserva__id", "referencia_externa")
    readonly_fields = ("creado_en", "actualizado_en")
