from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import LinkForm
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
                ('external_link', 'internal_link'),
            )
        }),
        (_('Link settings'), {
            'classes': ('collapse',),
            'fields': (
                ('mailto', 'phone'),
                ('anchor', 'target'),
                ('file_link'),
            ),
        }),
        (_('Advanced settings'), {
            'classes': ('collapse',),
            'fields': (
                'template',
                'attributes',
            )
        }),
    ]

    @classmethod
    def get_render_queryset(cls):
        queryset = super().get_render_queryset()
        return queryset.select_related('internal_link')

    def get_render_template(self, context, instance, placeholder):
        return f'djangocms_link/{instance.template}/link.html'

    def render(self, context, instance, placeholder):
        context['link'] = instance.get_link()
        return super().render(context, instance, placeholder)

    def get_form(self, request, obj=None, **kwargs):
        form_class = super().get_form(request, obj, **kwargs)

        if obj and obj.page and hasattr(obj.page, 'site') and obj.page.site:
            site = obj.page.site
        elif self.page and hasattr(self.page, 'site') and self.page.site:
            site = self.page.site
        else:
            site = Site.objects.get_current()

        class Form(form_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.for_site(site)

        return Form


plugin_pool.register_plugin(LinkPlugin)
