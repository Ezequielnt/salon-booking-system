from django.contrib import admin

from apps.pagos.models import Pago

from .models import Reserva


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("id", "espacio", "cliente", "inicio", "fin", "estado", "monto_total")
    list_filter = ("estado", "espacio__salon")
    search_fields = ("espacio__nombre", "cliente__username", "cliente__email")
    date_hierarchy = "inicio"
    readonly_fields = ("creado_en", "actualizado_en")
    inlines = [PagoInline]
