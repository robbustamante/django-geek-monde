"""
Development settings for Django Geek Monde.
Extends base settings with development-specific configuration.
"""
from .base import *  # noqa

# Override with development settings
DEBUG = True

ALLOWED_HOSTS = ['*']

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache - Simple local memory cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'geek-monde-dev',
    }
}

# Logging - More verbose for development
LOGGING['loggers'] = {
    'django': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'apps': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# CORS - Allow all for development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:8080',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
]

# REST Framework - Better error messages for development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
    'rest_framework.renderers.BrowsableAPIRenderer',
)

# Security - Relaxed for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CRSF_COOKIE_SECURE = False

# Static files - No compression for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
