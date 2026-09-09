import { Link, useParams } from "react-router-dom";

import { Cargando, ErrorMsg, Vacio } from "@/components/Estado";
import { IconArrowLeft, IconClock, IconUsers } from "@/components/icons";
import { traerSalon } from "@/features/salones/api";
import { formatMoney } from "@/lib/format";
import { useAsync } from "@/lib/useAsync";

export default function SalonDetallePage() {
  const { id } = useParams();
  const { data: salon, error, loading } = useAsync(() => traerSalon(id!), [id]);

  if (loading) return <Cargando />;
  if (error) return <ErrorMsg mensaje={error} />;
  if (!salon) return <Vacio texto="Salón no encontrado." />;

  return (
    <div className="stack">
      <Link to="/salones" className="back-link">
        <IconArrowLeft width={16} height={16} />
        Salones
      </Link>

      <div className="page-head">
        <div>
          <h1>{salon.nombre}</h1>
          <p className="muted" style={{ margin: "0.35rem 0 0" }}>
            {salon.direccion}
          </p>
        </div>
      </div>

      {salon.descripcion && <p style={{ maxWidth: "60ch" }}>{salon.descripcion}</p>}
      <p className="muted" style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.9rem" }}>
        <IconClock width={16} height={16} />
        Cancelación sin cargo hasta {salon.politica_cancelacion_horas} h antes del evento.
      </p>

      <h2 style={{ fontSize: "1.25rem", marginTop: "0.75rem" }}>Espacios</h2>
      {!salon.espacios.length ? (
        <Vacio texto="Este salón todavía no tiene espacios reservables." />
      ) : (
        <div className="grid-cards">
          {salon.espacios.map((espacio) => (
            <div key={espacio.id} className="card espacio-card">
              <h3>{espacio.nombre}</h3>
              {espacio.descripcion && (
                <p className="muted" style={{ margin: 0, fontSize: "0.88rem" }}>
                  {espacio.descripcion}
                </p>
              )}
              <ul className="espacio-card__specs">
                <li style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <IconUsers width={15} height={15} />
                  Hasta {espacio.capacidad} personas
                </li>
                <li>{formatMoney(espacio.precio_base)} de referencia</li>
              </ul>
              <Link className="btn" to={`/espacios/${espacio.id}`}>
                Ver disponibilidad
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
