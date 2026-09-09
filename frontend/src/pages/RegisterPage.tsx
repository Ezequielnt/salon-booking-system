import { useState, type ChangeEvent, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "@/features/auth/AuthContext";
import { apiError } from "@/lib/api";

export default function RegisterPage() {
  const { user, registro } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  if (user) return <Navigate to="/salones" replace />;

  const set =
    (campo: keyof typeof form) => (e: ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [campo]: e.target.value }));

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await registro(form);
      navigate("/salones", { replace: true });
    } catch (err) {
      setError(apiError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="stack">
      <h2 style={{ fontSize: "1.35rem" }}>Crear cuenta</h2>
      <form className="form" onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="username">Usuario</label>
          <input id="username" value={form.username} onChange={set("username")} required />
        </div>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={form.email} onChange={set("email")} required />
        </div>
        <div className="field">
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            type="password"
            value={form.password}
            onChange={set("password")}
            autoComplete="new-password"
            required
          />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
          <div className="field">
            <label htmlFor="first_name">Nombre</label>
            <input id="first_name" value={form.first_name} onChange={set("first_name")} />
          </div>
          <div className="field">
            <label htmlFor="last_name">Apellido</label>
            <input id="last_name" value={form.last_name} onChange={set("last_name")} />
          </div>
        </div>
        {error && <p className="error">{error}</p>}
        <button className="btn" type="submit" disabled={enviando}>
          {enviando ? "Creando…" : "Crear cuenta"}
        </button>
      </form>
      <p className="muted" style={{ fontSize: "0.9rem" }}>
        ¿Ya tenés cuenta? <Link to="/login">Ingresar</Link>
      </p>
    </div>
  );
}
