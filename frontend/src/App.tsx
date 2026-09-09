import { Suspense, lazy } from "react";
import { Route, Routes } from "react-router-dom";

import AppLayout from "@/components/AppLayout";
import { Cargando } from "@/components/Estado";
import ProtectedRoute from "@/components/ProtectedRoute";
import PublicLayout from "@/components/PublicLayout";
import HomePage from "@/pages/HomePage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import SalonDetallePage from "@/pages/SalonDetallePage";
import SalonesPage from "@/pages/SalonesPage";
import {
  CheckoutPage,
  MisReservasPage,
  NotFoundPage,
  PanelCalendarioPage,
  PanelReservasPage,
  PanelSalonPage,
} from "@/pages/stubs";

// FullCalendar es pesado: se carga solo al entrar a la pantalla del espacio.
const EspacioPage = lazy(() => import("@/pages/espacio/EspacioPage"));

export default function App() {
  return (
    <Suspense fallback={<Cargando />}>
      <Routes>
        {/* Sin sesión */}
        <Route element={<PublicLayout />}>
          <Route index element={<HomePage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="registro" element={<RegisterPage />} />
          <Route path="checkout/:token" element={<CheckoutPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>

        {/* Cliente + dueño */}
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="salones" element={<SalonesPage />} />
            <Route path="salones/:id" element={<SalonDetallePage />} />
            <Route path="espacios/:espacioId" element={<EspacioPage />} />
            <Route path="mis-reservas" element={<MisReservasPage />} />
          </Route>
        </Route>

        {/* Solo dueño */}
        <Route element={<ProtectedRoute rol="admin_salon" />}>
          <Route element={<AppLayout />}>
            <Route path="panel" element={<PanelSalonPage />} />
            <Route path="panel/reservas" element={<PanelReservasPage />} />
            <Route path="panel/calendario" element={<PanelCalendarioPage />} />
          </Route>
        </Route>
      </Routes>
    </Suspense>
  );
}
