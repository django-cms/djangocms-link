# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.models import CMSPlugin, Page

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djangocms_attributes_field.fields import AttributesField

from .validators import IntranetURLValidator


@python_2_unicode_compatible
class AbstractLink(CMSPlugin):
    """
    A link to an other page or to an external website
    """

    TARGET_CHOICES = (
        ('', _('same window')),
        ('_blank', _('new window')),
        ('_parent', _('parent window')),
        ('_top', _('topmost frame')),
    )

    # Used by django-cms search
    search_fields = ('name', )

    url_validators = [IntranetURLValidator(intranet_host_re=getattr(
        settings, 'DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN', None)), ]

    # Add an app namespace to related_name to avoid field name clashes
    # with any other plugins that have a field with the same name as the
    # lowercase of the class name of this model.
    # https://github.com/divio/django-cms/issues/5030
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin, related_name='%(app_label)s_%(class)s', parent_link=True)

    name = models.CharField(_('name'), max_length=256)
    # Re: max_length, see: http://stackoverflow.com/questions/417142/
    url = models.CharField(_('link'), blank=True, null=True,
                           validators=url_validators, max_length=2048)
    page_link = models.ForeignKey(
        Page,
        verbose_name=_('page'),
        blank=True,
        null=True,
        help_text=_('A link to a page has priority over a text link.'),
        on_delete=models.SET_NULL
    )
    anchor = models.CharField(_('anchor'), max_length=128, blank=True,
                              help_text=_('This applies only to page and text links.'
                                          ' Do <em>not</em> include a preceding "#" symbol.'))
    # Explicitly set a max_length so that we don't end up with different
    # schemata on Django 1.7 vs. 1.8.
    mailto = models.EmailField(_('email address'), max_length=254, blank=True, null=True,
                               help_text=_('An email address has priority over a text link.'))
    phone = models.CharField(_('Phone'), blank=True, null=True, max_length=40,
                             help_text=_('A phone number has priority over a mailto link.'))
    target = models.CharField(_('target'), blank=True, max_length=100,
                              choices=TARGET_CHOICES)

    # These attributes are already managed by other fields
    EXCLUDED_KEYS = [
        'href',
        'target',
    ]

    attributes = AttributesField(
        _('link tag attributes'), excluded_keys=EXCLUDED_KEYS, blank=True,
        help_text=_('Optional. Link HTML tag attributes'),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def link(self):
        if self.phone:
            link = 'tel:%s' % self.phone
        elif self.mailto:
            link = 'mailto:%s' % self.mailto
        elif self.url:
            link = self.url
        elif self.page_link_id:
            link = self.page_link.get_absolute_url()
        else:
            link = ''
        if (self.url or self.page_link or not link) and self.anchor:
            link += '#%s' % self.anchor
        return link


class Link(AbstractLink):

    class Meta:
        abstract = False
