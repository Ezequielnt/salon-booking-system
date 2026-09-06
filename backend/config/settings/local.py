"""Settings de desarrollo local. Es el módulo por defecto (ver manage.py)."""

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# django-extensions solo está en requirements/local.txt
INSTALLED_APPS += ["django_extensions"]  # noqa: F405

# En local mostramos los emails por consola salvo que se pida Mailhog.
EMAIL_BACKEND = env(  # noqa: F405
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
