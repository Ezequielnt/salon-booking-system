/** Cliente HTTP contra la API de DRF.
 *
 * - Adjunta el access token en cada request.
 * - Ante un 401, intenta refrescar el token una vez y reintenta el request.
 * - Si el refresh falla, limpia la sesión y emite `auth:logout` para que el
 *   AuthContext redirija al login.
 */

import axios, {
  AxiosError,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";

import { tokenStore } from "./tokens";

const baseURL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export const api = axios.create({ baseURL });

export const AUTH_LOGOUT_EVENT = "auth:logout";

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const access = tokenStore.access;
  if (access && config.headers) {
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

type RetriableConfig = AxiosRequestConfig & { _retry?: boolean };

let refreshing: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh = tokenStore.refresh;
  if (!refresh) throw new Error("sin refresh token");
  // Cliente aparte: sin interceptores, para no entrar en loop.
  const { data } = await axios.post(`${baseURL}/auth/token/refresh/`, {
    refresh,
  });
  tokenStore.set({ access: data.access, refresh: data.refresh });
  return data.access as string;
}

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined;
    const status = error.response?.status;
    const isAuthCall = original?.url?.includes("/auth/token");

    if (status === 401 && original && !original._retry && !isAuthCall) {
      original._retry = true;
      try {
        refreshing = refreshing ?? refreshAccessToken();
        const access = await refreshing;
        refreshing = null;
        original.headers = { ...original.headers, Authorization: `Bearer ${access}` };
        return api(original);
      } catch (refreshError) {
        refreshing = null;
        tokenStore.clear();
        window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  },
);

/** Extrae un mensaje legible de un AxiosError de DRF. */
export function apiError(error: unknown): string {
  if (!axios.isAxiosError(error)) return "Error inesperado.";
  const data = error.response?.data as
    | Record<string, unknown>
    | string
    | undefined;
  if (!data) return error.message;
  if (typeof data === "string") return data;
  if (typeof data.detail === "string") return data.detail;
  const first = Object.values(data)[0];
  if (Array.isArray(first)) return String(first[0]);
  if (typeof first === "string") return first;
  return "Revisá los datos e intentá de nuevo.";
}
