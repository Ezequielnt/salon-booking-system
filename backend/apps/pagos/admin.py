from django.contrib import admin, messages

from .models import EstadoPago, Pago, TransicionInvalida


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "reserva", "tipo", "monto", "estado", "proveedor", "creado_en")
    list_filter = ("tipo", "estado", "proveedor")
    search_fields = ("reserva__id", "referencia_externa")
    readonly_fields = ("estado", "creado_en", "actualizado_en")
    actions = ["aprobar", "rechazar", "reembolsar"]

    def _transicionar_seleccion(self, request, queryset, nuevo_estado):
        exitosos = 0
        for pago in queryset:
            try:
                pago.transicionar(nuevo_estado)
                exitosos += 1
            except TransicionInvalida as exc:
                self.message_user(request, f"Pago #{pago.pk}: {exc}", level=messages.ERROR)
        if exitosos:
            self.message_user(
                request,
                f"{exitosos} pago(s) pasaron a «{EstadoPago(nuevo_estado).label}».",
                level=messages.SUCCESS,
            )

    @admin.action(description="Aprobar pagos seleccionados")
    def aprobar(self, request, queryset):
        self._transicionar_seleccion(request, queryset, EstadoPago.APROBADO)

    @admin.action(description="Rechazar pagos seleccionados")
    def rechazar(self, request, queryset):
        self._transicionar_seleccion(request, queryset, EstadoPago.RECHAZADO)

    @admin.action(description="Reembolsar pagos seleccionados")
    def reembolsar(self, request, queryset):
        self._transicionar_seleccion(request, queryset, EstadoPago.REEMBOLSADO)
