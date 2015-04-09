from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.conf import settings

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from djangocms_link.models import Link


class LinkPlugin(CMSPluginBase):

    model = Link
    name = _("Link")
    render_template = "cms/plugins/link.html"
    text_enabled = True
    allow_children = True

    def render(self, context, instance, placeholder):
        link = instance.link()
        context.update({
            'name': instance.name,
            'link': link,
            'target': instance.target,
            'placeholder': placeholder,
            'object': instance
        })
        return context

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

    def icon_src(self, instance):
        return settings.STATIC_URL + u"cms/img/icons/plugins/link.png"

plugin_pool.register_plugin(LinkPlugin)
