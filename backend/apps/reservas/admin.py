from django.contrib import admin, messages

from apps.pagos.models import Pago

from .models import EstadoReserva, Reserva, TransicionInvalida


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("id", "espacio", "cliente", "inicio", "fin", "estado", "monto_total")
    list_filter = ("estado", "espacio__salon")
    search_fields = ("espacio__nombre", "cliente__username", "cliente__email")
    date_hierarchy = "inicio"
    readonly_fields = ("estado", "creado_en", "actualizado_en")
    inlines = [PagoInline]
    actions = ["confirmar", "cancelar", "completar"]

    def _transicionar_seleccion(self, request, queryset, nuevo_estado):
        exitosas = 0
        for reserva in queryset:
            try:
                reserva.transicionar(nuevo_estado)
                exitosas += 1
            except TransicionInvalida as exc:
                self.message_user(request, f"Reserva #{reserva.pk}: {exc}", level=messages.ERROR)
        if exitosas:
            self.message_user(
                request,
                f"{exitosas} reserva(s) pasaron a «{EstadoReserva(nuevo_estado).label}».",
                level=messages.SUCCESS,
            )

    @admin.action(description="Confirmar reservas seleccionadas")
    def confirmar(self, request, queryset):
        self._transicionar_seleccion(request, queryset, EstadoReserva.CONFIRMADA)

    @admin.action(description="Cancelar reservas seleccionadas")
    def cancelar(self, request, queryset):
        self._transicionar_seleccion(request, queryset, EstadoReserva.CANCELADA)

    @admin.action(description="Marcar reservas como completadas")
    def completar(self, request, queryset):
        self._transicionar_seleccion(request, queryset, EstadoReserva.COMPLETADA)