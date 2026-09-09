import { api } from "@/lib/api";

import type { DisponibilidadDia, EventoOcupacion } from "./types";

/** YYYY-MM-DD */
function fechaISO(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export async function traerOcupacion(
  espacioId: number | string,
  desde: Date,
  hasta: Date,
): Promise<EventoOcupacion[]> {
  const { data } = await api.get<EventoOcupacion[]>(
    `/espacios/${espacioId}/ocupacion/`,
    { params: { desde: fechaISO(desde), hasta: fechaISO(hasta) } },
  );
  return data;
}

export async function traerDisponibilidad(
  espacioId: number | string,
  fecha: string,
): Promise<DisponibilidadDia> {
  const { data } = await api.get<DisponibilidadDia>(
    `/espacios/${espacioId}/disponibilidad/`,
    { params: { fecha } },
  );
  return data;
}
