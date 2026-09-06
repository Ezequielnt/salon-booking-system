#!/bin/sh
set -e

# Solo el servicio "backend" corre migraciones y seed (RUN_MIGRATIONS=1).
# El worker y beat de Celery arrancan directo.
if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  echo "→ Aplicando migraciones..."
  python manage.py migrate --no-input

  echo "→ Cargando datos de demo (idempotente)..."
  python manage.py seed_demo
fi

exec "$@"
