FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Cliente de Postgres para debugging / pg_isready. psycopg[binary] trae sus wheels.
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias primero para aprovechar la cache de capas.
COPY requirements/ requirements/
ARG REQUIREMENTS=local
RUN pip install --upgrade pip \
    && pip install -r "requirements/${REQUIREMENTS}.txt"

COPY . .

RUN chmod +x /app/entrypoint.sh

# Correr como UID 1000 para que los archivos generados en el bind mount
# (migraciones, etc.) queden con el owner del host, no root.
RUN useradd --uid 1000 --create-home app && chown -R app:app /app
USER app

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
