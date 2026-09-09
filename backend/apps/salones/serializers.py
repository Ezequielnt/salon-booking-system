from rest_framework import serializers

from .models import Espacio, Salon


class EspacioSerializer(serializers.ModelSerializer):
    salon_nombre = serializers.CharField(source="salon.nombre", read_only=True)

    class Meta:
        model = Espacio
        fields = (
            "id",
            "salon",
            "salon_nombre",
            "nombre",
            "descripcion",
            "capacidad",
            "precio_base",
            "activo",
        )

    def validate_salon(self, salon):
        """Un admin_salon solo puede colgar espacios de sus propios salones."""
        user = self.context["request"].user
        if not user.is_staff and salon.owner_id != user.id:
            raise serializers.ValidationError("Ese salón no es tuyo.")
        return salon


class SalonSerializer(serializers.ModelSerializer):
    espacios = EspacioSerializer(many=True, read_only=True)

    class Meta:
        model = Salon
        fields = (
            "id",
            "nombre",
            "descripcion",
            "direccion",
            "politica_cancelacion_horas",
            "activo",
            "espacios",
        )
