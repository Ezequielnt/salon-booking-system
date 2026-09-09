import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "@/features/auth/AuthContext";
import { apiError } from "@/lib/api";

export default function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const destino =
    (location.state as { from?: Location } | null)?.from?.pathname ?? "/salones";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  if (user) return <Navigate to={destino} replace />;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await login({ username, password });
      navigate(destino, { replace: true });
    } catch (err) {
      setError(apiError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="stack">
      <h2 style={{ fontSize: "1.35rem" }}>Ingresar</h2>
      <form className="form" onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="username">Usuario</label>
          <input
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </div>
        <div className="field">
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>
        {error && <p className="error">{error}</p>}
        <button className="btn" type="submit" disabled={enviando}>
          {enviando ? "Ingresando…" : "Ingresar"}
        </button>
      </form>
      <p className="muted" style={{ fontSize: "0.9rem" }}>
        ¿No tenés cuenta? <Link to="/registro">Crear una</Link>
      </p>
      <p className="muted" style={{ fontSize: "0.8rem" }}>
        Demo: <code>cliente / demo1234</code> · <code>dueno / demo1234</code>
      </p>
    </div>
  );
}
