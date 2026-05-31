"""
Core CMS Cascade plugins and extensions.
This module extends django-cms-cascade functionality for the Geek Monde store.
"""
from django.utils.translation import gettext_lazy as _
from cmsplugin_cascade.generic.cms_plugins import TextLinkPlugin
from cmsplugin_cascade.link.plugin_base import LinkPluginBase


class CoreLinkPluginBase(LinkPluginBase):
    """
    Base link plugin for core cascade plugins.
    Extends the standard cascade link functionality.
    """
    pass
