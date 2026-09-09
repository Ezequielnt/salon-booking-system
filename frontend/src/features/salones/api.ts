import { api } from "@/lib/api";
import type { Paginated } from "@/lib/pagination";

import type { Espacio, Salon } from "./types";

export async function listarSalones(): Promise<Salon[]> {
  const { data } = await api.get<Paginated<Salon>>("/salones/");
  return data.results;
}

export async function traerSalon(id: number | string): Promise<Salon> {
  const { data } = await api.get<Salon>(`/salones/${id}/`);
  return data;
}

export async function traerEspacio(id: number | string): Promise<Espacio> {
  const { data } = await api.get<Espacio>(`/espacios/${id}/`);
  return data;
}
