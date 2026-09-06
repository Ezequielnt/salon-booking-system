"""
Settings tipo producción. La demo NO se despliega; queda como referencia
y para que la imagen Docker "prod" sea representativa.

Activar con: DJANGO_SETTINGS_MODULE=config.settings.production
"""

from .base import *  # noqa: F401,F403

DEBUG = False

# Whitenoise sirve los estáticos sin un nginx aparte.
MIDDLEWARE.insert(  # noqa: F405
    1, "whitenoise.middleware.WhiteNoiseMiddleware"
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Endurecimiento básico detrás de un proxy TLS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
