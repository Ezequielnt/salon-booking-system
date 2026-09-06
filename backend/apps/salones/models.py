from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.usuarios.models import Rol


class Salon(models.Model):
    """Un salón de eventos. Pertenece a un usuario con rol admin_salon
    y agrupa uno o más espacios reservables."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="salones",
        limit_choices_to={"rol": Rol.ADMIN_SALON},
        verbose_name="propietario",
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    direccion = models.CharField("dirección", max_length=255)
    politica_cancelacion_horas = models.PositiveIntegerField(
        "horas mínimas para cancelar",
        default=48,
        help_text="Antelación mínima para cancelar una reserva sin penalidad.",
    )
    activo = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "salón"
        verbose_name_plural = "salones"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Espacio(models.Model):
    """Unidad reservable dentro de un salón (ej: "Salón principal",
    "Jardín", "Terraza"). Cada espacio tiene su propio calendario."""

    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name="espacios",
        verbose_name="salón",
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    capacidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Precio de referencia. El monto final de la reserva puede diferir.",
    )
    activo = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "espacio"
        verbose_name_plural = "espacios"
        ordering = ["salon__nombre", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["salon", "nombre"],
                name="espacio_nombre_unico_por_salon",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nombre} — {self.salon.nombre}"
