from django import template

from djangocms_link.helpers import get_link


register = template.Library()


@register.filter
def to_url(value):
    return get_link(value) or ""


@register.simple_tag
def get_url(value):
    return to_url(value)
