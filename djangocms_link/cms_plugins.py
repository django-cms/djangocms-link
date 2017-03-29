# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

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

    @classmethod
    def get_render_queryset(cls):
        queryset = super(LinkPlugin, cls).get_render_queryset()
        return queryset.select_related('internal_link')

    def get_render_template(self, context, instance, placeholder):
        return 'djangocms_link/{}/link.html'.format(instance.template)

    def render(self, context, instance, placeholder):
        context['link'] = instance.get_link()
        return super(LinkPlugin, self).render(context, instance, placeholder)

    def get_form(self, request, obj=None, **kwargs):
        form_class = super(LinkPlugin, self).get_form(request, obj, **kwargs)

        if obj and obj.page and obj.page.site:
            site = obj.page.site
        elif self.page and self.page.site:
            site = self.page.site
        else:
            # this might NOT give the result you expect
            site = Site.objects.get_current()

        class Form(form_class):
            def __init__(self, *args, **kwargs):
                super(Form, self).__init__(*args, **kwargs)
                self.for_site(site)

        return Form


plugin_pool.register_plugin(LinkPlugin)
