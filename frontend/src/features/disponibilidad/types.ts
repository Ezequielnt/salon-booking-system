export interface EventoOcupacion {
  inicio: string;
  fin: string;
  tipo: "reserva" | "bloqueo";
  detalle: string;
}

export interface Intervalo {
  inicio: string;
  fin: string;
}

export interface DisponibilidadDia {
  fecha: string;
  abierto: boolean;
  dia_semana?: string;
  franjas: Intervalo[];
  ocupado: EventoOcupacion[];
  libre: Intervalo[];
}
