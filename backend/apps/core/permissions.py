"""Permisos compartidos por las apps de la API.

El modelo de acceso tiene tres roles (ver `apps.usuarios.models.Rol`):

- ``admin_salon``: administra SUS salones, espacios, reglas y bloqueos, y
  gestiona las reservas y pagos de esos espacios.
- ``cliente``: navega salones/espacios activos y crea/ve sus propias reservas.
- ``staff`` / superuser: acceso amplio (se usa desde el Django admin sobre todo).

El aislamiento multi-tenant real se resuelve filtrando el queryset en cada
ViewSet (ver ``get_queryset``), no solo con estos permisos.
"""

from rest_framework import permissions

from apps.usuarios.models import Rol


class EsAdminSalon(permissions.BasePermission):
    """Solo usuarios autenticados con rol ``admin_salon`` (o staff/superuser)."""

    message = "Necesitás ser administrador de salón para hacer esto."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_staff or user.rol == Rol.ADMIN_SALON)
        )


class SoloLecturaOAdminSalon(permissions.BasePermission):
    """Lectura para cualquier autenticado; escritura solo ``admin_salon``.

    Pensado para los recursos que el cliente consulta pero no modifica
    (salones, espacios, reglas de disponibilidad).
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(user.is_staff or user.rol == Rol.ADMIN_SALON)
