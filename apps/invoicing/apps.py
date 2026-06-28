"""
AppConfig for the invoicing app.
"""
from django.apps import AppConfig


class InvoicingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.invoicing'
    verbose_name = 'Facturación Electrónica SIFEN'

    def ready(self):
        import apps.invoicing.signals  # noqa: F401
