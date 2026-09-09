export type Rol = "admin_salon" | "cliente" | "staff";

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  rol: Rol;
}

export interface Credenciales {
  username: string;
  password: string;
}

export interface DatosRegistro {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}
