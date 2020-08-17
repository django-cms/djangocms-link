"""
Enables the user to add a "Link" plugin that displays a link
using the HTML <a> tag.
"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from cms.models import CMSPlugin, Page

from djangocms_attributes_field.fields import AttributesField
from filer.fields.file import FilerFileField

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
    # re: max_length, see: http://stackoverflow.com/questions/417142/
    external_link = models.CharField(
        verbose_name=_('External link'),
        blank=True,
        max_length=2040,
        validators=url_validators,
        help_text=_('Provide a link to an external source.'),
    )
    internal_link = models.ForeignKey(
        Page,
        verbose_name=_('Internal link'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_('If provided, overrides the external link.'),
    )
    file_link = FilerFileField(
        verbose_name=_('File link'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_('If provided links a file from the filer app.'),
    )
    # other link types
    anchor = models.CharField(
        verbose_name=_('Anchor'),
        blank=True,
        max_length=255,
        help_text=_('Appends the value only after the internal or external link. '
                    'Do <em>not</em> include a preceding "#" symbol.'),
    )
    mailto = models.EmailField(
        verbose_name=_('Email address'),
        blank=True,
        max_length=255,
    )
    phone = models.CharField(
        verbose_name=_('Phone'),
        blank=True,
        max_length=255,
    )
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
        if self.name and self.get_link():
            return '{} ({})'.format(self.name, self.get_link())
        return self.name or self.get_link() or gettext('<link is missing>')

    def get_link(self):
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
                link = '//{}{}'.format(ref_site, link)

        elif self.file_link:
            link = self.file_link.url

        elif self.external_link:
            link = self.external_link

        elif self.phone:
            link = 'tel:{}'.format(self.phone.replace(' ', ''))

        elif self.mailto:
            link = 'mailto:{}'.format(self.mailto)

        else:
            link = ''

        if (not self.phone and not self.mailto) and self.anchor:
            link += '#{}'.format(self.anchor)

        return link

    def clean(self):
        super().clean()
        field_names = (
            'external_link',
            'internal_link',
            'mailto',
            'phone',
            'file_link',
        )
        anchor_field_name = 'anchor'
        field_names_allowed_with_anchor = (
            'external_link',
            'internal_link',
        )

        anchor_field_verbose_name = force_text(
           self._meta.get_field(anchor_field_name).verbose_name)
        anchor_field_value = getattr(self, anchor_field_name)

        link_fields = {
            key: getattr(self, key)
            for key in field_names
        }
        link_field_verbose_names = {
            key: force_text(self._meta.get_field(key).verbose_name)
            for key in link_fields.keys()
        }
        provided_link_fields = {
            key: value
            for key, value in link_fields.items()
            if value
        }

        if len(provided_link_fields) > 1:
            # Too many fields have a value.
            verbose_names = sorted(link_field_verbose_names.values())
            error_msg = _('Only one of {0} or {1} may be given.').format(
                ', '.join(verbose_names[:-1]),
                verbose_names[-1],
            )
            errors = {}.fromkeys(provided_link_fields.keys(), error_msg)
            raise ValidationError(errors)

        if (len(provided_link_fields) == 0
                and not self.anchor
                and not self.link_is_optional):

            raise ValidationError(
                _('Please provide a link.')
            )

        if anchor_field_value:
            for field_name in provided_link_fields.keys():
                if field_name not in field_names_allowed_with_anchor:
                    error_msg = _('%(anchor_field_verbose_name)s is not allowed together with %(field_name)s') % {
                        'anchor_field_verbose_name': anchor_field_verbose_name,
                        'field_name': link_field_verbose_names.get(field_name)
                    }
                    raise ValidationError({
                        anchor_field_name: error_msg,
                        field_name: error_msg,
                    })


class Link(AbstractLink):

    class Meta:
        abstract = False
