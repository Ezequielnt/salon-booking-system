import { useEffect, type ReactNode } from "react";

export default function Modal({
  titulo,
  onClose,
  children,
}: {
  titulo: string;
  onClose: () => void;
  children: ReactNode;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  return (
    <div
      className="modal"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="modal__card" role="dialog" aria-modal="true" aria-label={titulo}>
        <div className="modal__head">
          <h3>{titulo}</h3>
          <button className="modal__x" onClick={onClose} aria-label="Cerrar">
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
