from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.TextChoices):
    ADMIN_SALON = "admin_salon", "Administrador de salón"
    CLIENTE = "cliente", "Cliente"
    STAFF = "staff", "Staff"


class User(AbstractUser):
    """Usuario del sistema.

    El rol define qué puede hacer:
    - admin_salon: administra sus propios salones y espacios.
    - cliente: navega salones y crea reservas.
    - staff: personal del salón (permisos acotados, se define más adelante).
    """

    email = models.EmailField("correo electrónico", unique=True)
    rol = models.CharField(
        "rol",
        max_length=20,
        choices=Rol.choices,
        default=Rol.CLIENTE,
    )

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self) -> str:
        return f"{self.get_username()} ({self.get_rol_display()})"

    @property
    def es_admin_salon(self) -> bool:
        return self.rol == Rol.ADMIN_SALON
