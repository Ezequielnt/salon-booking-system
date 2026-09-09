export type EstadoReserva = "pendiente" | "confirmada" | "cancelada" | "completada";

export interface Reserva {
  id: number;
  espacio: number;
  espacio_nombre: string;
  salon_nombre: string;
  cliente: number;
  inicio: string;
  fin: string;
  estado: EstadoReserva;
  estado_display: string;
  monto_total: string;
  notas: string;
  total_pagado: string;
  saldo_pendiente: string;
  puede_cancelarse: boolean;
  creado_en: string;
}

export interface NuevaReserva {
  espacio: number;
  inicio: string;
  fin: string;
  notas?: string;
}
