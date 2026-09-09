import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "@/features/auth/AuthContext";

/** Envuelve rutas que requieren sesión. `rol="admin_salon"` además exige ese rol. */
export default function ProtectedRoute({ rol }: { rol?: "admin_salon" }) {
  const { user, cargando, esAdminSalon } = useAuth();
  const location = useLocation();

  if (cargando) return <p className="muted">Cargando…</p>;

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (rol === "admin_salon" && !esAdminSalon) {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}
