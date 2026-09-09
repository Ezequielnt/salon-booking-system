const money = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
  maximumFractionDigits: 0,
});

/** "150000.00" -> "$ 150.000" */
export function formatMoney(valor: string | number): string {
  return money.format(Number(valor));
}

const fechaLarga = new Intl.DateTimeFormat("es-AR", {
  weekday: "long",
  day: "numeric",
  month: "long",
});

const hora = new Intl.DateTimeFormat("es-AR", {
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

export function formatFecha(iso: string): string {
  const s = fechaLarga.format(new Date(iso));
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function formatHora(iso: string): string {
  return hora.format(new Date(iso));
}

export function formatRango(inicioIso: string, finIso: string): string {
  return `${formatHora(inicioIso)}–${formatHora(finIso)}`;
}
