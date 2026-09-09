/** Estados de carga / error / vacío reutilizables. */

export function Cargando({ texto = "Cargando…" }: { texto?: string }) {
  return <p className="muted">{texto}</p>;
}

export function ErrorMsg({ mensaje }: { mensaje: string }) {
  return <p className="error">{mensaje}</p>;
}

export function Vacio({ texto }: { texto: string }) {
  return <p className="muted">{texto}</p>;
}
