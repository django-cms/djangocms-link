from django import template

from djangocms_link.helpers import LinkDict, get_link


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
    return LinkDict(value)
