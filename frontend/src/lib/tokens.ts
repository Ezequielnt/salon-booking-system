/** Persistencia de los tokens JWT en localStorage.
 *
 * Para una demo alcanza. En producción el refresh token debería ir en una
 * cookie httpOnly para que no lo pueda leer un XSS.
 */

const ACCESS = "sb.access";
const REFRESH = "sb.refresh";

export const tokenStore = {
  get access() {
    return localStorage.getItem(ACCESS);
  },
  get refresh() {
    return localStorage.getItem(REFRESH);
  },
  set({ access, refresh }: { access: string; refresh?: string }) {
    localStorage.setItem(ACCESS, access);
    if (refresh) localStorage.setItem(REFRESH, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS);
    localStorage.removeItem(REFRESH);
  },
};
