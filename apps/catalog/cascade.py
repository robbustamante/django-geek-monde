"""
Catalog CMS Plugin configurations.
"""
from cmsplugin_cascade.link.plugin_base import LinkPluginBase

class CatalogLinkPluginBase(LinkPluginBase):
    """
    Custom link plugin for catalog items.
    Allows CMS to link directly to Product and Category models.
    """
    # This is a minimal bridge to satisfy the settings import.
    # We will expand this with actual link fields later.
    pass
