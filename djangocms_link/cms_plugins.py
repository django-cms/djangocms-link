from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .helpers import get_link
from .models import Link


class LinkPlugin(CMSPluginBase):
    model = Link
    name = _('Link')
    text_enabled = True
    allow_children = True

    fieldsets = [
        (None, {
            'fields': (
                'name',
                'link',
                'target',
            )
        }),
        (_('Advanced settings'), {
            'classes': ('collapse',),
            'fields': (
                'template',
                'attributes',
            )
        }),
    ]

    def get_render_template(self, context, instance, placeholder):
        return f'djangocms_link/{instance.template}/link.html'

    def render(self, context, instance, placeholder):
        context['link'] = get_link(instance.link, getattr(get_current_site(context["request"]), "id", None))
        return super().render(context, instance, placeholder)


plugin_pool.register_plugin(LinkPlugin)
