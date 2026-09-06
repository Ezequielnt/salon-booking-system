from django.contrib import admin

from .models import BloqueoFecha, ReglaDisponibilidad


@admin.register(ReglaDisponibilidad)
class ReglaDisponibilidadAdmin(admin.ModelAdmin):
    list_display = ("espacio", "dia_semana", "hora_inicio", "hora_fin")
    list_filter = ("dia_semana", "espacio__salon")
    search_fields = ("espacio__nombre",)


@admin.register(BloqueoFecha)
class BloqueoFechaAdmin(admin.ModelAdmin):
    list_display = ("espacio", "inicio", "fin", "motivo")
    list_filter = ("espacio__salon",)
    search_fields = ("espacio__nombre", "motivo")
