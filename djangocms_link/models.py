# -*- coding: utf-8 -*-
"""
Enables the user to add a "Link" plugin that displays a link
using the HTML <a> tag.
"""
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _

from cms.models import CMSPlugin, Page

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

@python_2_unicode_compatible
class AbstractLink(CMSPlugin):
    # used by django CMS search
    search_fields = ('name', )

    url_validators = [IntranetURLValidator(intranet_host_re=HOSTNAME),]

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
    external_link = models.URLField(
        verbose_name=_('External link'),
        blank=True,
        max_length=2040,
        validators=url_validators,
        help_text=_('Provide a valid URL to an external website.'),
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
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name or str(self.pk)

    def get_short_description(self):
        if self.name:
            return '{} ({})'.format(self.name, self.get_link())
        return self.get_link() or ugettext('<link is missing>')

    def get_link(self):
        if self.phone:
            link = 'tel:{}'.format(self.phone.replace(' ', ''))
        elif self.mailto:
            link = 'mailto:{}'.format(self.mailto)
        elif self.external_link:
            link = self.external_link
        elif self.internal_link_id:
            link = self.internal_link.get_absolute_url()
        else:
            link = ''
        if (not self.phone and not self.mailto) and self.anchor:
            link += '#{}'.format(self.anchor)

        return link


class Link(AbstractLink):

    class Meta:
        abstract = False
