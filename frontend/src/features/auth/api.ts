import { api } from "@/lib/api";
import { tokenStore } from "@/lib/tokens";

import type { Credenciales, DatosRegistro, User } from "./types";

export async function obtenerToken(cred: Credenciales): Promise<void> {
  const { data } = await api.post("/auth/token/", cred);
  tokenStore.set({ access: data.access, refresh: data.refresh });
}

export async function registrar(datos: DatosRegistro): Promise<void> {
  await api.post("/auth/registro/", datos);
}

export async function traerUsuario(): Promise<User> {
  const { data } = await api.get<User>("/auth/me/");
  return data;
}
