"""App de Celery. Se importa desde config/__init__.py para que quede
disponible al arrancar Django."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("salon")

# Toda la config de Celery vive en settings con prefijo CELERY_.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descubre tasks.py en cada app instalada.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
