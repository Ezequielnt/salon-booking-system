import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { Cargando, ErrorMsg, Vacio } from "@/components/Estado";
import { IconBuilding } from "@/components/icons";
import { listarSalones } from "@/features/salones/api";
import type { Salon } from "@/features/salones/types";
import { formatMoney } from "@/lib/format";
import { useAsync } from "@/lib/useAsync";

function precioDesde(salon: Salon): number | null {
  if (!salon.espacios.length) return null;
  return Math.min(...salon.espacios.map((e) => Number(e.precio_base)));
}

export default function SalonesPage() {
  const { data: salones, error, loading } = useAsync(listarSalones, []);
  const [params] = useSearchParams();
  const q = (params.get("q") ?? "").toLowerCase();
  const [vista, setVista] = useState<"cards" | "list">("cards");

  const filtrados = useMemo(() => {
    if (!salones) return [];
    if (!q) return salones;
    return salones.filter(
      (s) =>
        s.nombre.toLowerCase().includes(q) ||
        s.direccion.toLowerCase().includes(q),
    );
  }, [salones, q]);

  return (
    <div className="stack">
      <div className="page-head">
        <h1>Salones</h1>
        <div className="page-head__actions">
          <div className="segmented">
            <button
              className={vista === "list" ? "active" : ""}
              onClick={() => setVista("list")}
            >
              Lista
            </button>
            <button
              className={vista === "cards" ? "active" : ""}
              onClick={() => setVista("cards")}
            >
              Tarjetas
            </button>
          </div>
        </div>
      </div>

      {loading && <Cargando />}
      {error && <ErrorMsg mensaje={error} />}
      {!loading && !error && !filtrados.length && (
        <Vacio
          texto={q ? `Ningún salón coincide con «${params.get("q")}».` : "Todavía no hay salones."}
        />
      )}

      {!loading && !error && filtrados.length > 0 && vista === "cards" && (
        <div className="grid-cards">
          {filtrados.map((salon) => {
            const desde = precioDesde(salon);
            return (
              <Link key={salon.id} to={`/salones/${salon.id}`} className="salon-card">
                <div className="salon-card__cover">
                  <IconBuilding width={28} height={28} />
                </div>
                <div className="salon-card__body">
                  <h3>{salon.nombre}</h3>
                  <p className="muted" style={{ margin: 0, fontSize: "0.88rem" }}>
                    {salon.direccion}
                  </p>
                  <p className="salon-card__meta">
                    {salon.espacios.length} espacio
                    {salon.espacios.length === 1 ? "" : "s"}
                    {desde !== null && <> · desde {formatMoney(desde)}</>}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {!loading && !error && filtrados.length > 0 && vista === "list" && (
        <div className="card" style={{ padding: 0, overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                <th>Salón</th>
                <th>Dirección</th>
                <th>Espacios</th>
                <th>Desde</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {filtrados.map((salon) => {
                const desde = precioDesde(salon);
                return (
                  <tr key={salon.id}>
                    <td style={{ fontWeight: 600 }}>{salon.nombre}</td>
                    <td className="muted">{salon.direccion}</td>
                    <td>{salon.espacios.length}</td>
                    <td>{desde !== null ? formatMoney(desde) : "—"}</td>
                    <td style={{ textAlign: "right" }}>
                      <Link className="btn ghost" to={`/salones/${salon.id}`}>
                        Ver
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
