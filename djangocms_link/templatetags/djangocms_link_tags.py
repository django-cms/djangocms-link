from django import template
from django.db import models

from djangocms_link.helpers import get_link


try:
    from filer.models import File
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    class File:
        pass


register = template.Library()


@register.filter
def to_url(value):
    return get_link(value) or ""


@register.filter
def to_link(value):
    if isinstance(value, File):
        return {"file_link": value.pk}
    elif isinstance(value, models.Model):
        return {"internal_link": f"{value._meta.app_label}.{value._meta.model_name}:{value.pk}"}
    return {"external_link": value}
