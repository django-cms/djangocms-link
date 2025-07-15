from django import template
from django.db import models

from djangocms_link.helpers import LinkDict, get_link, get_obj_link


try:
    from filer.models import File
except (ImportError, ModuleNotFoundError):  # pragma: no cover

    class File:
        pass


register = template.Library()


@register.filter
def to_url(value):
    if isinstance(value, models.Model):
        return get_obj_link(value) or ""
    elif isinstance(value, dict):
        return get_link(value) or ""
    return ""


@register.filter
def to_link(value):
    return LinkDict(value)
