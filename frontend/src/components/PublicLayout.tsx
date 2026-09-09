import { Link, Outlet } from "react-router-dom";

import { IconLeaf } from "./icons";

/** Layout para pantallas sin sesión: tarjeta centrada sobre el lienzo verde. */
export default function PublicLayout() {
  return (
    <div className="public">
      <div className="public__card">
        <Link
          to="/"
          className="public__brand"
          style={{ textDecoration: "none", color: "inherit" }}
        >
          <IconLeaf />
          Salón Booking
        </Link>
        <Outlet />
      </div>
    </div>
  );
}
