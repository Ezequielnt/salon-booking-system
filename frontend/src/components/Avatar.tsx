/** Círculo con las iniciales del usuario. */
export default function Avatar({ nombre }: { nombre: string }) {
  const iniciales = nombre
    .split(/[\s.@_-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0]?.toUpperCase())
    .join("");
  return <span className="avatar">{iniciales || "?"}</span>;
}
