from django.contrib import admin

from .models import Espacio, Salon


class EspacioInline(admin.TabularInline):
    model = Espacio
    extra = 1


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ("nombre", "owner", "activo", "politica_cancelacion_horas")
    list_filter = ("activo",)
    search_fields = ("nombre", "direccion", "owner__username")
    inlines = [EspacioInline]


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "salon", "capacidad", "precio_base", "activo")
    list_filter = ("activo", "salon")
    search_fields = ("nombre", "salon__nombre")
