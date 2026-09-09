import { Link, Navigate } from "react-router-dom";

import { useAuth } from "@/features/auth/AuthContext";

export default function HomePage() {
  const { user, esAdminSalon } = useAuth();

  if (user) return <Navigate to={esAdminSalon ? "/panel" : "/salones"} replace />;

  return (
    <div className="stack">
      <h1 style={{ fontSize: "1.6rem" }}>Reservá tu salón</h1>
      <p className="muted">
        Elegí un espacio, mirá el calendario, reservá y pagá la seña. Todo desde
        acá.
      </p>
      <div style={{ display: "grid", gap: "0.6rem", marginTop: "0.5rem" }}>
        <Link className="btn" to="/login">
          Ingresar
        </Link>
        <Link className="btn secondary" to="/registro">
          Crear cuenta
        </Link>
      </div>
      <p className="muted" style={{ fontSize: "0.82rem", marginTop: "1rem" }}>
        Demo: <code>cliente / demo1234</code> · <code>dueno / demo1234</code>
      </p>
    </div>
  );
}
