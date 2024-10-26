from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import LinkForm
from .helpers import get_link
from .models import Link


class LinkPlugin(CMSPluginBase):
    model = Link
    form = LinkForm
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

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)

        if obj and obj.page and hasattr(obj.page, 'site') and obj.page.site:
            site = obj.page.site
        elif self.page and hasattr(self.page, 'site') and self.page.site:
            site = self.page.site
        else:
            site = get_current_site(request)

        class Form(form_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.for_site(site)

        return Form


plugin_pool.register_plugin(LinkPlugin)
