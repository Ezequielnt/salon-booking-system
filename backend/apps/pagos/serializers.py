from rest_framework import serializers

from apps.reservas.models import Reserva

from .models import Pago


class PagoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Pago
        fields = (
            "id",
            "reserva",
            "tipo",
            "monto",
            "estado",
            "estado_display",
            "tipo_display",
            "proveedor",
            "referencia_externa",
            "creado_en",
        )
        read_only_fields = ("estado", "proveedor", "referencia_externa", "creado_en")

    def validate_reserva(self, reserva: Reserva):
        user = self.context["request"].user
        propia = reserva.cliente_id == user.id
        del_salon = reserva.espacio.salon.owner_id == user.id
        if not (user.is_staff or propia or del_salon):
            raise serializers.ValidationError("Esa reserva no es tuya.")
        return reserva

    def validate_monto(self, monto):
        if monto <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero.")
        return monto
