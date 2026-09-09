from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Rol

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Datos públicos del usuario logueado (`/auth/me/`)."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "rol")
        read_only_fields = fields


class RegistroSerializer(serializers.ModelSerializer):
    """Alta self-service. Siempre crea un usuario con rol `cliente`:
    el rol `admin_salon` se asigna desde el Django admin."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(rol=Rol.CLIENTE, **validated_data)
        user.set_password(password)
        user.save()
        return user
