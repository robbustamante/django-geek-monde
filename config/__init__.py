"""
Django Geek Monde - E-commerce Platform for Geek Clothing and Articles
"""
__version__ = '1.0.0'

# Make Celery app available when Django starts
from .celery import app as celery_app  # noqa

__all__ = ('celery_app',)
