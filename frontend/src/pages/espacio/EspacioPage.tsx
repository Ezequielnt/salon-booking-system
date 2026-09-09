import { useCallback, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import FullCalendar from "@fullcalendar/react";
import type {
  DateSelectArg,
  EventInput,
  EventSourceFuncArg,
} from "@fullcalendar/core";
import esLocale from "@fullcalendar/core/locales/es";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";

import { Cargando, ErrorMsg, Vacio } from "@/components/Estado";
import { IconArrowLeft } from "@/components/icons";
import { traerOcupacion } from "@/features/disponibilidad/api";
import { traerEspacio } from "@/features/salones/api";
import { formatMoney } from "@/lib/format";
import { useAsync } from "@/lib/useAsync";

import ReservaDialog from "./ReservaDialog";
import "./calendario.css";

export default function EspacioPage() {
  const { espacioId } = useParams();
  const { data: espacio, error, loading } = useAsync(
    () => traerEspacio(espacioId!),
    [espacioId],
  );
  const calRef = useRef<FullCalendar>(null);
  const [seleccion, setSeleccion] = useState<{ inicio: Date; fin: Date } | null>(null);

  const cargarEventos = useCallback(
    async (
      info: EventSourceFuncArg,
      success: (events: EventInput[]) => void,
      failure: (err: Error) => void,
    ) => {
      try {
        const eventos = await traerOcupacion(espacioId!, info.start, info.end);
        success(
          eventos.map((e) => ({
            title: e.tipo === "bloqueo" ? e.detalle || "Bloqueado" : "Reservado",
            start: e.inicio,
            end: e.fin,
            classNames: [e.tipo === "bloqueo" ? "ev-bloqueo" : "ev-reserva"],
          })),
        );
      } catch (err) {
        failure(err instanceof Error ? err : new Error(String(err)));
      }
    },
    [espacioId],
  );

  function onSelect(arg: DateSelectArg) {
    setSeleccion({ inicio: arg.start, fin: arg.end });
    calRef.current?.getApi().unselect();
  }

  if (loading) return <Cargando />;
  if (error) return <ErrorMsg mensaje={error} />;
  if (!espacio) return <Vacio texto="Espacio no encontrado." />;

  return (
    <div className="stack">
      <Link to={`/salones/${espacio.salon}`} className="back-link">
        <IconArrowLeft width={16} height={16} />
        {espacio.salon_nombre}
      </Link>

      <div className="page-head">
        <div>
          <h1>{espacio.nombre}</h1>
          <p className="muted" style={{ margin: "0.35rem 0 0" }}>
            Hasta {espacio.capacidad} personas · {formatMoney(espacio.precio_base)} de referencia
          </p>
        </div>
      </div>

      <p className="muted" style={{ fontSize: "0.9rem" }}>
        Elegí un rango libre en el calendario para reservar. Los bloques grises ya
        están ocupados.
      </p>

      <div className="card calendario">
        <FullCalendar
          ref={calRef}
          plugins={[timeGridPlugin, dayGridPlugin, interactionPlugin]}
          initialView="timeGridWeek"
          locale={esLocale}
          headerToolbar={{
            left: "prev,next today",
            center: "title",
            right: "timeGridWeek,dayGridMonth",
          }}
          slotMinTime="08:00:00"
          slotMaxTime="24:00:00"
          allDaySlot={false}
          nowIndicator
          selectable
          selectMirror
          selectOverlap={false}
          selectAllow={(span) => span.start >= new Date()}
          select={onSelect}
          events={cargarEventos}
          height="auto"
          expandRows
        />
      </div>

      {seleccion && (
        <ReservaDialog
          espacio={espacio}
          inicio={seleccion.inicio}
          fin={seleccion.fin}
          onClose={() => setSeleccion(null)}
          onCreada={() => calRef.current?.getApi().refetchEvents()}
        />
      )}
    </div>
  );
}
