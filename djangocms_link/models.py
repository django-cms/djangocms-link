"""
Enables the user to add a "Link" plugin that displays a link
using the HTML <a> tag.
"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_str
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from cms.models import CMSPlugin

from djangocms_attributes_field.fields import AttributesField

from .fields import LinkField
from .helpers import get_link
from .validators import IntranetURLValidator


# Add additional choices through the ``settings.py``.
def get_templates():
    choices = [
        ('default', _('Default')),
    ]
    choices += getattr(
        settings,
        'DJANGOCMS_LINK_TEMPLATES',
        [],
    )
    return choices


HOSTNAME = getattr(
    settings,
    'DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN',
    None
)

TARGET_CHOICES = (
    ('_blank', _('Open in new window')),
    ('_self', _('Open in same window')),
    ('_parent', _('Delegate to parent')),
    ('_top', _('Delegate to top')),
)


class AbstractLink(CMSPlugin):
    # used by django CMS search
    search_fields = ('name', )

    # allows link requirement to be changed when another
    # CMS plugin inherits from AbstractLink
    link_is_optional = False

    url_validators = [
        IntranetURLValidator(intranet_host_re=HOSTNAME),
    ]

    template = models.CharField(
        verbose_name=_('Template'),
        choices=get_templates(),
        default=get_templates()[0][0],
        max_length=255,
    )
    name = models.CharField(
        verbose_name=_('Display name'),
        blank=True,
        max_length=255,
    )

    link = LinkField(
        verbose_name=_('Link'),
    )
    # # re: max_length, see: http://stackoverflow.com/questions/417142/
    #
    # external_link = models.CharField(
    #     verbose_name=_('External link'),
    #     blank=True,
    #     max_length=2040,
    #     validators=url_validators,
    #     help_text=_('Provide a link to an external source.'),
    # )
    # internal_link = models.ForeignKey(
    #     Page,
    #     verbose_name=_('Internal link'),
    #     blank=True,
    #     null=True,
    #     on_delete=models.SET_NULL,
    #     help_text=_('If provided, overrides the external link.'),
    # )
    # file_link = FilerFileField(
    #     verbose_name=_('File link'),
    #     blank=True,
    #     null=True,
    #     on_delete=models.SET_NULL,
    #     help_text=_('If provided links a file from the filer app.'),
    # )
    # # other link types
    # anchor = models.CharField(
    #     verbose_name=_('Anchor'),
    #     blank=True,
    #     max_length=255,
    #     help_text=_('Appends the value only after the internal or external link. '
    #                 'Do <em>not</em> include a preceding "#" symbol.'),
    # )
    # mailto = models.EmailField(
    #     verbose_name=_('Email address'),
    #     blank=True,
    #     max_length=255,
    # )
    # phone = models.CharField(
    #     verbose_name=_('Phone'),
    #     blank=True,
    #     max_length=255,
    # )
    # advanced options
    target = models.CharField(
        verbose_name=_('Target'),
        choices=TARGET_CHOICES,
        blank=True,
        max_length=255,
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
        excluded_keys=['href', 'target'],
    )

    # Add an app namespace to related_name to avoid field name clashes
    # with any other plugins that have a field with the same name as the
    # lowercase of the class name of this model.
    # https://github.com/divio/django-cms/issues/5030
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin,
        related_name='%(app_label)s_%(class)s',
        parent_link=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name or str(self.pk)

    def get_short_description(self):
        link = self.get_link()
        if self.name and link:
            return f'{self.name} ({link})'
        return self.name or link or gettext('<link is missing>')

    def get_link(self, site=None):
        return get_link(self.link, site)

        if self.internal_link:
            ref_page = self.internal_link
            link = ref_page.get_absolute_url()

            # simulate the call to the unauthorized CMSPlugin.page property
            cms_page = self.placeholder.page if self.placeholder_id else None

            # first, we check if the placeholder the plugin is attached to
            # has a page. Thus the check "is not None":
            if cms_page is not None:
                if getattr(cms_page, 'node', None):
                    cms_page_site_id = getattr(cms_page.node, 'site_id', None)
                else:
                    cms_page_site_id = getattr(cms_page, 'site_id', None)
            # a plugin might not be attached to a page and thus has no site
            # associated with it. This also applies to plugins inside
            # static placeholders
            else:
                cms_page_site_id = None

            # now we do the same for the reference page the plugin links to
            # in order to compare them later
            if cms_page is not None:
                if getattr(cms_page, 'node', None):
                    ref_page_site_id = ref_page.node.site_id
                else:
                    ref_page_site_id = ref_page.site_id
            # if no external reference is found the plugin links to the
            # current page
            else:
                ref_page_site_id = Site.objects.get_current().pk

            if ref_page_site_id != cms_page_site_id:
                ref_site = Site.objects._get_site_by_id(ref_page_site_id).domain
                link = f'//{ref_site}{link}'

        elif self.file_link:
            link = self.file_link.url

        elif self.external_link:
            link = self.external_link

        elif self.phone:
            link = 'tel:{}'.format(self.phone.replace(' ', ''))

        elif self.mailto:
            link = f'mailto:{self.mailto}'

        else:
            link = ''

        if (not self.phone and not self.mailto) and self.anchor:
            link += f'#{self.anchor}'

        return link

    def clean(self):
        super().clean()
        if not self.link_is_optional and not self.link:
            raise ValidationError(
                force_str(_('Link is required.')),
                code='required',
            )


class Link(AbstractLink):
    class Meta:
        abstract = False
