from django.contrib import admin

from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("id", "reserva", "tipo", "enviado", "fecha_envio")
    list_filter = ("tipo", "enviado")
    search_fields = ("reserva__id",)
    readonly_fields = ("creado_en",)
