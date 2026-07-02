"""
Production settings for Django Geek Monde.
Extends base settings with production-specific security and performance settings.
"""
from .base import *  # noqa
import environ

env = environ.Env()

# Override with production settings
DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Database - PostgreSQL for production
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='postgresql://user:password@localhost:5432/geek_monde'
    )
}

# Cache - Redis for production
CACHES = {
    'default': env.cache(
        'CACHE_URL',
        default='redis://localhost:6379/1'
    )
}

# Email - Real SMTP for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
STAMPED_ACCEPT_LANGUAGE_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Logging - File-based for production
LOGGING['handlers']['file'] = {
    'level': 'INFO',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': BASE_DIR / 'logs' / 'django.log',
    'maxBytes': 1024 * 1024 * 15,  # 15MB
    'backupCount': 10,
    'formatter': 'verbose',
}

LOGGING['root']['handlers'] = ['file']

# Static files - WhiteNoise for efficient serving
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# CORS - Only allowed hosts
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=[]
)
