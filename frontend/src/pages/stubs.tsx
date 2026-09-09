/** Pantallas todavía no implementadas. Se completan en los próximos pasos:
 *  calendario del espacio (FullCalendar), flujo de reserva/checkout,
 *  mis reservas, panel del salón (dashboard, reservas entrantes, calendario).
 */

function Stub({ titulo }: { titulo: string }) {
  return (
    <div className="stack">
      <div className="page-head">
        <h1>{titulo}</h1>
      </div>
      <p className="muted">Próximamente.</p>
    </div>
  );
}

export const CheckoutPage = () => <Stub titulo="Pago" />;
export const MisReservasPage = () => <Stub titulo="Mis reservas" />;
export const PanelSalonPage = () => <Stub titulo="Panel" />;
export const PanelReservasPage = () => <Stub titulo="Reservas entrantes" />;
export const PanelCalendarioPage = () => <Stub titulo="Calendario" />;

export function NotFoundPage() {
  return (
    <div className="stack" style={{ textAlign: "center" }}>
      <h1>404</h1>
      <p className="muted">Esa página no existe.</p>
    </div>
  );
}
