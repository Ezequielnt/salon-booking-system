import { useState } from "react";
import { Link } from "react-router-dom";

import Modal from "@/components/Modal";
import { crearReserva } from "@/features/reservas/api";
import type { Reserva } from "@/features/reservas/types";
import type { Espacio } from "@/features/salones/types";
import { apiError } from "@/lib/api";
import { formatFecha, formatMoney, formatRango } from "@/lib/format";

interface Props {
  espacio: Espacio;
  inicio: Date;
  fin: Date;
  onClose: () => void;
  onCreada: () => void;
}

export default function ReservaDialog({ espacio, inicio, fin, onClose, onCreada }: Props) {
  const [notas, setNotas] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [reserva, setReserva] = useState<Reserva | null>(null);

  async function reservar() {
    setError(null);
    setEnviando(true);
    try {
      const r = await crearReserva({
        espacio: espacio.id,
        inicio: inicio.toISOString(),
        fin: fin.toISOString(),
        notas: notas.trim() || undefined,
      });
      setReserva(r);
      onCreada();
    } catch (err) {
      setError(apiError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Modal titulo={reserva ? "Reserva creada" : "Reservar espacio"} onClose={onClose}>
      {reserva ? (
        <div className="stack">
          <p>
            Tu reserva quedó <strong>pendiente</strong>. Confirmá pagando la seña
            desde tus reservas.
          </p>
          <dl className="resumen">
            <div>
              <dt>Total</dt>
              <dd>{formatMoney(reserva.monto_total)}</dd>
            </div>
            <div>
              <dt>Saldo</dt>
              <dd>{formatMoney(reserva.saldo_pendiente)}</dd>
            </div>
          </dl>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Link className="btn" to="/mis-reservas">
              Ir a mis reservas
            </Link>
            <button className="btn secondary" onClick={onClose}>
              Seguir mirando
            </button>
          </div>
        </div>
      ) : (
        <div className="stack">
          <dl className="resumen">
            <div>
              <dt>Espacio</dt>
              <dd>
                {espacio.nombre} · {espacio.salon_nombre}
              </dd>
            </div>
            <div>
              <dt>Fecha</dt>
              <dd>{formatFecha(inicio.toISOString())}</dd>
            </div>
            <div>
              <dt>Horario</dt>
              <dd>{formatRango(inicio.toISOString(), fin.toISOString())}</dd>
            </div>
            <div>
              <dt>Precio</dt>
              <dd>{formatMoney(espacio.precio_base)}</dd>
            </div>
          </dl>
          <div className="field">
            <label htmlFor="notas">Notas (opcional)</label>
            <input
              id="notas"
              value={notas}
              onChange={(e) => setNotas(e.target.value)}
              placeholder="Cumpleaños, 50 personas…"
            />
          </div>
          {error && <p className="error">{error}</p>}
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button className="btn" onClick={reservar} disabled={enviando}>
              {enviando ? "Reservando…" : "Reservar"}
            </button>
            <button className="btn secondary" onClick={onClose} disabled={enviando}>
              Cancelar
            </button>
          </div>
        </div>
      )}
    </Modal>
  );
}
