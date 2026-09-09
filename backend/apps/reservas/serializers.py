from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import serializers

from apps.salones.models import Espacio

from .models import EstadoReserva, Reserva


class ReservaSerializer(serializers.ModelSerializer):
    espacio_nombre = serializers.CharField(source="espacio.nombre", read_only=True)
    salon_nombre = serializers.CharField(source="espacio.salon.nombre", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    total_pagado = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    saldo_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    puede_cancelarse = serializers.BooleanField(read_only=True)

    class Meta:
        model = Reserva
        fields = (
            "id",
            "espacio",
            "espacio_nombre",
            "salon_nombre",
            "cliente",
            "inicio",
            "fin",
            "estado",
            "estado_display",
            "monto_total",
            "notas",
            "total_pagado",
            "saldo_pendiente",
            "puede_cancelarse",
            "creado_en",
        )
        read_only_fields = ("cliente", "estado", "monto_total", "creado_en")

    def validate_espacio(self, espacio):
        if not espacio.activo or not espacio.salon.activo:
            raise serializers.ValidationError("Ese espacio no está disponible.")
        return espacio

    def validate(self, attrs):
        # En update, completar los campos que no vienen con los de la instancia.
        inicio = attrs.get("inicio", getattr(self.instance, "inicio", None))
        fin = attrs.get("fin", getattr(self.instance, "fin", None))
        espacio = attrs.get("espacio", getattr(self.instance, "espacio", None))

        if self.instance and self.instance.estado != EstadoReserva.PENDIENTE:
            if {"inicio", "fin", "espacio"} & set(attrs):
                raise serializers.ValidationError(
                    "Solo se puede reprogramar una reserva mientras está pendiente."
                )

        if inicio and fin and espacio:
            disponible = espacio.esta_disponible(
                inicio, fin, excluir_reserva_id=self.instance.pk if self.instance else None
            )
            if not disponible:
                raise serializers.ValidationError(
                    "El espacio no está disponible en ese horario "
                    "(fuera de horario, bloqueado, o ya reservado)."
                )
        return attrs

    def create(self, validated_data):
        espacio: Espacio = validated_data["espacio"]
        validated_data["cliente"] = self.context["request"].user
        validated_data["monto_total"] = espacio.precio_base
        try:
            return super().create(validated_data)
        except IntegrityError:
            # La ExclusionConstraint de la DB: alguien reservó el mismo hueco
            # entre la validación y el insert.
            raise serializers.ValidationError(
                "Ese horario se acaba de ocupar. Probá con otro."
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
