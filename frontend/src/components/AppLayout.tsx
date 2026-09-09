import { useState, type FormEvent } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "@/features/auth/AuthContext";

import Avatar from "./Avatar";
import {
  IconBuilding,
  IconCalendar,
  IconGrid,
  IconLeaf,
  IconLogout,
  IconSearch,
  IconTicket,
} from "./icons";

interface NavDef {
  to: string;
  label: string;
  icon: JSX.Element;
  end?: boolean;
}

const NAV_CLIENTE: NavDef[] = [
  { to: "/salones", label: "Salones", icon: <IconBuilding /> },
  { to: "/mis-reservas", label: "Mis reservas", icon: <IconTicket /> },
];

const NAV_DUENO: NavDef[] = [
  { to: "/panel", label: "Panel", icon: <IconGrid />, end: true },
  { to: "/salones", label: "Salones", icon: <IconBuilding /> },
  { to: "/panel/reservas", label: "Reservas", icon: <IconTicket /> },
  { to: "/panel/calendario", label: "Calendario", icon: <IconCalendar /> },
];

export default function AppLayout() {
  const { user, esAdminSalon, logout } = useAuth();
  const navigate = useNavigate();
  const [q, setQ] = useState("");

  const items = esAdminSalon ? NAV_DUENO : NAV_CLIENTE;

  function buscar(e: FormEvent) {
    e.preventDefault();
    navigate(q.trim() ? `/salones?q=${encodeURIComponent(q.trim())}` : "/salones");
  }

  return (
    <div className="shell">
      <div className="shell__inner">
        <aside className="sidebar">
          <div className="sidebar__brand">
            <IconLeaf />
            Salón Booking
          </div>
          <nav className="sidebar__nav">
            {items.map((it) => (
              <NavLink key={it.to} to={it.to} end={it.end} className="nav-item">
                {it.icon}
                <span>{it.label}</span>
              </NavLink>
            ))}
          </nav>
          <div className="sidebar__foot">
            <button className="sidebar__logout" onClick={logout}>
              <IconLogout />
              <span>Salir</span>
            </button>
          </div>
        </aside>

        <div className="main">
          <header className="topbar">
            <form className="search" onSubmit={buscar}>
              <IconSearch width={18} height={18} />
              <input
                placeholder="Buscar salones…"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                aria-label="Buscar salones"
              />
            </form>
            <div className="user-chip">
              <span>{user?.username}</span>
              <Avatar nombre={user?.username ?? "?"} />
            </div>
          </header>
          <div className="content">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  );
}
