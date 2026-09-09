export interface Espacio {
  id: number;
  salon: number;
  salon_nombre: string;
  nombre: string;
  descripcion: string;
  capacidad: number;
  precio_base: string;
  activo: boolean;
}

export interface Salon {
  id: number;
  nombre: string;
  descripcion: string;
  direccion: string;
  politica_cancelacion_horas: number;
  activo: boolean;
  espacios: Espacio[];
}
