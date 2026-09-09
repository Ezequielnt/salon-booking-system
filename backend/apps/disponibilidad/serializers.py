from rest_framework import serializers

from .models import BloqueoFecha, ReglaDisponibilidad


class _EspacioPropioMixin:
    """Valida que el espacio referenciado pertenezca al admin_salon que llama."""

    def validate_espacio(self, espacio):
        user = self.context["request"].user
        if not user.is_staff and espacio.salon.owner_id != user.id:
            raise serializers.ValidationError("Ese espacio no es tuyo.")
        return espacio


class ReglaDisponibilidadSerializer(_EspacioPropioMixin, serializers.ModelSerializer):
    class Meta:
        model = ReglaDisponibilidad
        fields = ("id", "espacio", "dia_semana", "hora_inicio", "hora_fin")

    def validate(self, attrs):
        inicio = attrs.get("hora_inicio", getattr(self.instance, "hora_inicio", None))
        fin = attrs.get("hora_fin", getattr(self.instance, "hora_fin", None))
        if inicio and fin and inicio >= fin:
            raise serializers.ValidationError("La hora de inicio debe ser anterior a la de fin.")
        return attrs


class BloqueoFechaSerializer(_EspacioPropioMixin, serializers.ModelSerializer):
    class Meta:
        model = BloqueoFecha
        fields = ("id", "espacio", "inicio", "fin", "motivo")

    def validate(self, attrs):
        inicio = attrs.get("inicio", getattr(self.instance, "inicio", None))
        fin = attrs.get("fin", getattr(self.instance, "fin", None))
        if inicio and fin and inicio >= fin:
            raise serializers.ValidationError("El inicio debe ser anterior al fin.")
        return attrs


# --- Respuestas de solo lectura de los endpoints de disponibilidad ---------


class IntervaloSerializer(serializers.Serializer):
    inicio = serializers.DateTimeField()
    fin = serializers.DateTimeField()


class EventoOcupacionSerializer(serializers.Serializer):
    inicio = serializers.DateTimeField()
    fin = serializers.DateTimeField()
    tipo = serializers.CharField()
    detalle = serializers.CharField()


class DisponibilidadDiaSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    abierto = serializers.BooleanField()
    dia_semana = serializers.CharField(required=False)
    franjas = IntervaloSerializer(many=True)
    ocupado = EventoOcupacionSerializer(many=True)
    libre = IntervaloSerializer(many=True)
