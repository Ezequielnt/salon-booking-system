import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export default function App() {
  const [estado, setEstado] = useState("comprobando API…");

  useEffect(() => {
    fetch(`${API_URL}/schema/`)
      .then((r) => setEstado(r.ok ? "conectado ✓" : `respondió ${r.status}`))
      .catch(() => setEstado("no disponible ✗"));
  }, []);

  return (
    <main
      style={{
        fontFamily: "system-ui, sans-serif",
        maxWidth: 640,
        margin: "0 auto",
        padding: "2rem",
        lineHeight: 1.5,
      }}
    >
      <h1>Salón Booking</h1>
      <p>Demo de sistema de reservas de salones de eventos.</p>
      <p>
        Backend: <strong>{estado}</strong>
      </p>
      <ul>
        <li>
          <a href="http://localhost:8000/admin/">Admin de Django</a> — admin / admin
        </li>
        <li>
          <a href="http://localhost:8000/api/v1/docs/">Documentación de la API (Swagger)</a>
        </li>
        <li>
          <a href="http://localhost:8025/">Mailpit</a> — emails de prueba
        </li>
      </ul>
      <p style={{ color: "#666" }}>
        El calendario (FullCalendar) y el flujo de reserva se implementan más adelante.
      </p>
    </main>
  );
}
