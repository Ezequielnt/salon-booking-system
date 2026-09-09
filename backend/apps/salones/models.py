from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

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

    def esta_disponible(self, inicio, fin, *, excluir_reserva_id=None) -> bool:
        """True si este espacio puede reservarse en [inicio, fin).

        Combina las tres fuentes de disponibilidad: la regla recurrente
        (horario del día), que no caiga en un bloqueo puntual, y que no
        pise otra reserva activa. No reemplaza al ExclusionConstraint de
        `Reserva` en la DB — esto da un error de validación legible antes
        de llegar ahí; la constraint sigue siendo la última barrera.
        """
        inicio_local = timezone.localtime(inicio)
        fin_local = timezone.localtime(fin)
        if inicio_local.date() != fin_local.date():
            return False

        dentro_de_regla = self.reglas_disponibilidad.filter(
            dia_semana=inicio_local.weekday(),
            hora_inicio__lte=inicio_local.time(),
            hora_fin__gte=fin_local.time(),
        ).exists()
        if not dentro_de_regla:
            return False

        hay_bloqueo = self.bloqueos.filter(inicio__lt=fin, fin__gt=inicio).exists()
        if hay_bloqueo:
            return False

        from apps.reservas.models import ESTADOS_QUE_OCUPAN

        reservas_choque = self.reservas.filter(
            estado__in=ESTADOS_QUE_OCUPAN,
            inicio__lt=fin,
            fin__gt=inicio,
        )
        if excluir_reserva_id:
            reservas_choque = reservas_choque.exclude(pk=excluir_reserva_id)
        return not reservas_choque.exists()
