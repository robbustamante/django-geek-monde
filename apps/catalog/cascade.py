"""
Catalog CMS Cascade plugins and extensions.
This module extends django-cms-cascade functionality for product catalog.
"""
from django.utils.translation import gettext_lazy as _
from cmsplugin_cascade.link.plugin_base import LinkPluginBase


class CatalogLinkPluginBase(LinkPluginBase):
    """
    Custom link plugin for catalog items.
    Allows creating links to products and categories in the CMS.
    """
    pass
