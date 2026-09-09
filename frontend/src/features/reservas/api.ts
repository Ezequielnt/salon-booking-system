import { api } from "@/lib/api";
import type { Paginated } from "@/lib/pagination";

import type { NuevaReserva, Reserva } from "./types";

export async function crearReserva(datos: NuevaReserva): Promise<Reserva> {
  const { data } = await api.post<Reserva>("/reservas/", datos);
  return data;
}

export async function listarMisReservas(): Promise<Reserva[]> {
  const { data } = await api.get<Paginated<Reserva>>("/reservas/");
  return data.results;
}

export async function traerReserva(id: number | string): Promise<Reserva> {
  const { data } = await api.get<Reserva>(`/reservas/${id}/`);
  return data;
}

type Accion = "confirmar" | "cancelar" | "completar";

export async function accionReserva(
  id: number | string,
  accion: Accion,
): Promise<Reserva> {
  const { data } = await api.post<Reserva>(`/reservas/${id}/${accion}/`);
  return data;
}
