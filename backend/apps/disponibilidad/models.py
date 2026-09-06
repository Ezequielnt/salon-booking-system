from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class DiaSemana(models.IntegerChoices):
    LUNES = 0, "Lunes"
    MARTES = 1, "Martes"
    MIERCOLES = 2, "Miércoles"
    JUEVES = 3, "Jueves"
    VIERNES = 4, "Viernes"
    SABADO = 5, "Sábado"
    DOMINGO = 6, "Domingo"


class ReglaDisponibilidad(models.Model):
    """Franja horaria recurrente en la que un espacio PUEDE reservarse.
    Si un espacio no tiene reglas para un día, ese día no es reservable."""

    espacio = models.ForeignKey(
        "salones.Espacio",
        on_delete=models.CASCADE,
        related_name="reglas_disponibilidad",
    )
    dia_semana = models.IntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        verbose_name = "regla de disponibilidad"
        verbose_name_plural = "reglas de disponibilidad"
        ordering = ["espacio", "dia_semana", "hora_inicio"]
        constraints = [
            models.CheckConstraint(
                condition=Q(hora_inicio__lt=F("hora_fin")),
                name="regla_hora_inicio_antes_de_fin",
            ),
        ]

    def clean(self):
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la de fin.")

    def __str__(self) -> str:
        return (
            f"{self.espacio} · {self.get_dia_semana_display()} "
            f"{self.hora_inicio:%H:%M}–{self.hora_fin:%H:%M}"
        )


class BloqueoFecha(models.Model):
    """Rango concreto en el que un espacio NO puede reservarse
    (mantenimiento, evento privado, feriado). Pisa a las reglas."""

    espacio = models.ForeignKey(
        "salones.Espacio",
        on_delete=models.CASCADE,
        related_name="bloqueos",
    )
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    motivo = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "bloqueo de fecha"
        verbose_name_plural = "bloqueos de fecha"
        ordering = ["-inicio"]
        constraints = [
            models.CheckConstraint(
                condition=Q(inicio__lt=F("fin")),
                name="bloqueo_inicio_antes_de_fin",
            ),
        ]

    def clean(self):
        if self.inicio and self.fin and self.inicio >= self.fin:
            raise ValidationError("El inicio debe ser anterior al fin.")

    def __str__(self) -> str:
        return f"{self.espacio} bloqueado {self.inicio:%d/%m %H:%M}–{self.fin:%H:%M}"
