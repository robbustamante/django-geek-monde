"""
Base settings for Django Geek Monde project.
These settings are common to all environments.
"""
import os
import sys
from pathlib import Path

from django.utils.translation import gettext_lazy as _
import environ

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = BASE_DIR / 'apps'

# Environment variables
env = environ.Env()
env.read_env(str(BASE_DIR / '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
DJANGO_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'django_filters',
    'rest_framework.authtoken',
    'drf_spectacular',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'django_fsm',
    'filer',
    'easy_thumbnails',
    'email_auth',
    'adminsortable2',
    'django_select2',
    'post_office',
]

LOCAL_APPS = [
    'apps.core',
    'apps.catalog',
    'apps.reviews',
    'apps.discounts',
    'apps.cart',
    'apps.order',
    'apps.payment',
    'apps.shipping',
    'apps.customer',
    'apps.inventory',
    'apps.notifications',
    'apps.invoicing',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'config.settings.base.ExceptionLoggingMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.gzip.GZipMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.csrf',
                'django.template.context_processors.i18n',
            ],
        },
    },
    {
        'BACKEND': 'post_office.template.backends.post_office.PostOfficeTemplates',
        'APP_DIRS': True,
        'DIRS': [BASE_DIR / 'templates'],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
            ]
        }
    },
]

# Database
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='sqlite:///db.sqlite3'
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es'
LANGUAGES = [
    ('es', _('Spanish')),
    ('en', _('English')),
    ('pt', _('Portuguese')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'America/Asuncion'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Django 5.x uses STORAGES instead of STATICFILES_STORAGE
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sites framework
SITE_ID = 1

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# DRF Spectacular (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Geek Monde API',
    'DESCRIPTION': 'API REST de comercio electrónico para indumentaria y artículos geek',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CORS Settings
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:3000', 'http://localhost:8000']
)
CORS_ALLOW_CREDENTIALS = True

# Authentication
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_USER_MODEL = 'email_auth.User'

# Allauth settings
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'

# Cache
CACHES = {
    'default': env.cache(
        'CACHE_URL',
        default='locmemcache://'
    )
}

# Sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email
EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@geek-monde.com')

# Django Post Office
POST_OFFICE = {
    'TEMPLATE_ENGINE': 'post_office',
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Thumbnail settings
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)
THUMBNAIL_PRESERVE_EXTENSIONS = True

# Django FSM
FSM_ADMIN_ACTIONS_PERMISSION = 'change'

# Shop-specific settings
SHOP_APP_LABEL = 'geek_monde'
DEFAULT_CURRENCY = 'PYG'

SHOP_CART_MODIFIERS = [
    'apps.cart.modifiers.DefaultCartModifier',
    'apps.cart.modifiers.TaxCartModifier',
    'apps.payment.modifiers.PayInAdvanceModifier',
]

SHOP_ORDER_WORKFLOWS = [
    'apps.payment.workflows.ManualPaymentWorkflowMixin',
    'apps.payment.workflows.CancelOrderWorkflowMixin',
    'apps.shipping.workflows.PartialDeliveryWorkflowMixin',
]

# Security settings
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
}
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Silent system checks
SILENCED_SYSTEM_CHECKS = ['auth.W004']

# Stripe Configuration
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')

# SIFEN - Facturación Electrónica Paraguay (DNIT)
SIFEN_TIMBRADO = env('SIFEN_TIMBRADO', default='12345678')
SIFEN_ESTABLECIMIENTO = env('SIFEN_ESTABLECIMIENTO', default='001')
SIFEN_PUNTO_EXPEDICION = env('SIFEN_PUNTO_EXPEDICION', default='001')
SIFEN_RUC_EMISOR = env('SIFEN_RUC_EMISOR', default='80012345-1')
SIFEN_RAZON_SOCIAL = env('SIFEN_RAZON_SOCIAL', default='Geek Monde S.A.')
SIFEN_NOMBRE_FANTASIA = env('SIFEN_NOMBRE_FANTASIA', default='Geek Monde')
SIFEN_DIRECCION = env('SIFEN_DIRECCION', default='Av. España 1234, Asunción, Paraguay')
SIFEN_TELEFONO = env('SIFEN_TELEFONO', default='+595 21 000000')
SIFEN_EMAIL = env('SIFEN_EMAIL', default='facturacion@geek-monde.com.py')
SIFEN_ACTIVIDAD = env('SIFEN_ACTIVIDAD', default='Comercio de indumentaria y artículos geek')
SIFEN_TIPO_CONTRIBUYENTE = env('SIFEN_TIPO_CONTRIBUYENTE', default='2')  # 1=Fisica, 2=Juridica
# URL de consulta KuDE (simulada para ejemplo)
SIFEN_EKUATIA_URL = 'https://ekuatia.set.gov.py/consultas/qr'

# MercadoPago Configuration
MERCADOPAGO_ACCESS_TOKEN = env('MERCADOPAGO_ACCESS_TOKEN', default='')

# Celery Configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Beat schedule para tareas periódicas
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-abandoned-carts': {
        'task': 'apps.notifications.tasks.check_abandoned_carts',
        'schedule': crontab(minute=0),  # Cada hora
    },
    'check-low-stock': {
        'task': 'apps.notifications.tasks.check_low_stock',
        'schedule': crontab(minute=0, hour='*/6'),  # Cada 6 horas
    },
}

class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        import traceback
        with open('error_debug.txt', 'w') as f:
            f.write(traceback.format_exc())
        return None

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://192.168.56.1:3000',
]
