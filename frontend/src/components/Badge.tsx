type Tono = "warn" | "ok" | "bad" | "neutral";

/** Píldora de estado. Mapea los estados del backend a un tono de color. */
const TONO: Record<string, Tono> = {
  pendiente: "warn",
  confirmada: "ok",
  aprobado: "ok",
  completada: "neutral",
  cancelada: "bad",
  rechazado: "bad",
  reembolsado: "neutral",
};

export default function Badge({
  estado,
  texto,
}: {
  estado: string;
  texto?: string;
}) {
  const tono = TONO[estado] ?? "neutral";
  const clase = tono === "neutral" ? "badge" : `badge badge--${tono}`;
  return <span className={clase}>{texto ?? estado}</span>;
}
