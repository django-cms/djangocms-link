# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.models import CMSPlugin, Page

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djangocms_attributes_field.fields import AttributesField

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

TYPE_CHOICES = (
    ('anchor', '<a>'),
    ('button', '<button>'),
) + getattr(
    settings,
    'DJANGOCMS_LINK_TYPES',
    ()
)

STYLE_CHOICES = getattr(
    settings,
    'DJANGOCMS_LINK_STYLES',
    (
        ('', _('<not configured>')),
    )
)

TARGET_CHOICES = (
    ('_blank', _('Open in new window')),
    ('_self', _('Open in same window')),
    ('_parent', _('Delegate to parent')),
    ('_top', _('Delegate to top')),
)


@python_2_unicode_compatible
class AbstractLink(CMSPlugin):
    """
    A link to an other page or to an external website
    """
    # Used by django-cms search
    search_fields = ('name', )

    url_validators = [IntranetURLValidator(intranet_host_re=getattr(
        settings, 'DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN', None)), ]

    template = models.CharField(
        verbose_name=_('Template'),
        choices=get_templates(),
        default=get_templates()[0][0],
        max_length=255,
    )
    name = models.CharField(
        verbose_name=_('Name'),
        blank=True,
        max_length=255,
    )
    # Re: max_length, see: http://stackoverflow.com/questions/417142/
    external_link = models.URLField(
        verbose_name=_('External link'),
        blank=True,
        null=True,
        max_length=2040,
        validators=url_validators,
        help_text=_('Provide a valid url to an external website.'),
    )
    internal_link = models.ForeignKey(
        Page,
        verbose_name=_('Internal link'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_('If provided, overrides the external link.'),
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
        null=True,
        max_length=255,
    )
    phone = models.CharField(
        verbose_name=_('Phone'),
        blank=True,
        null=True,
        max_length=255,
    )
    # advanced options
    target = models.CharField(
        verbose_name=_('Target'),
        choices=TARGET_CHOICES,
        blank=True,
        max_length=255,
    )
    styles = models.CharField(
        verbose_name=_('Styles'),
        choices=STYLE_CHOICES,
        blank=True,
        max_length=255,
        help_text=_('Optional style choices to be appended to "class". '
            'Use "Attributes" to set addtional classes or styles.'),
    )
    link_type = models.CharField(
        verbose_name=_('Link type'),
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES[0][0],
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
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def clean(self):
        if not self.external_link or self.internal_link:
            raise ValidationError(_('Error'))
        # cleaned_data = super(LinkForm, self).clean()
        # url = cleaned_data.get('url')
        # internal_link = cleaned_data.get('internal_link')
        # mailto = cleaned_data.get('mailto')
        # phone = cleaned_data.get('phone')
        # anchor = cleaned_data.get('anchor')
        # if not any([url, internal_link, mailto, phone, anchor]):
        #     raise ValidationError(_('At least one link is required.'))
        # return cleaned_data

    def link(self):
        if self.phone:
            link = 'tel:%s' % self.phone
        elif self.mailto:
            link = 'mailto:%s' % self.mailto
        elif self.external_link:
            link = self.external_link
        elif self.internal_link_id:
            link = self.internal_link.get_absolute_url()
        else:
            link = ''
        if (self.external_link or self.internal_link or not link) and self.anchor:
            link += '#%s' % self.anchor
        return link


class Link(AbstractLink):

    class Meta:
        abstract = False
