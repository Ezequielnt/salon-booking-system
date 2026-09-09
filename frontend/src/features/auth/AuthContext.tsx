import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { AUTH_LOGOUT_EVENT } from "@/lib/api";
import { tokenStore } from "@/lib/tokens";

import { obtenerToken, registrar, traerUsuario } from "./api";
import type { Credenciales, DatosRegistro, User } from "./types";

interface AuthContextValue {
  user: User | null;
  cargando: boolean;
  login: (cred: Credenciales) => Promise<void>;
  registro: (datos: DatosRegistro) => Promise<void>;
  logout: () => void;
  esAdminSalon: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [cargando, setCargando] = useState(true);

  const cargarUsuario = useCallback(async () => {
    if (!tokenStore.access) {
      setUser(null);
      setCargando(false);
      return;
    }
    try {
      setUser(await traerUsuario());
    } catch {
      tokenStore.clear();
      setUser(null);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    cargarUsuario();
  }, [cargarUsuario]);

  // El interceptor de axios emite este evento cuando el refresh falla.
  useEffect(() => {
    const onLogout = () => setUser(null);
    window.addEventListener(AUTH_LOGOUT_EVENT, onLogout);
    return () => window.removeEventListener(AUTH_LOGOUT_EVENT, onLogout);
  }, []);

  const login = useCallback(
    async (cred: Credenciales) => {
      await obtenerToken(cred);
      await cargarUsuario();
    },
    [cargarUsuario],
  );

  const registro = useCallback(
    async (datos: DatosRegistro) => {
      await registrar(datos);
      await obtenerToken({ username: datos.username, password: datos.password });
      await cargarUsuario();
    },
    [cargarUsuario],
  );

  const logout = useCallback(() => {
    tokenStore.clear();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      cargando,
      login,
      registro,
      logout,
      esAdminSalon: user?.rol === "admin_salon" || user?.rol === "staff",
    }),
    [user, cargando, login, registro, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
