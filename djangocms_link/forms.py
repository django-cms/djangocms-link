# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _

from djangocms_attributes_field.widgets import AttributesWidget

from .fields import PageSearchField
from .models import Link


class LinkForm(ModelForm):
    internal_link = PageSearchField(
        label=_('Internal link'),
        required=False,
    )

    def for_site(self, site):
        # override the internal_link fields queryset to contains just pages for
        # current site
        # this will work for PageSelectFormField
        from cms.models import Page
        self.fields['internal_link'].queryset = Page.objects.drafts().on_site(site)
        # set the current site as a internal_link field instance attribute
        # this will be used by the field later to properly set up the queryset
        # this will work for PageSearchField
        self.fields['internal_link'].site = site
        self.fields['internal_link'].widget.site = site

    class Meta:
        model = Link
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')

    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        self.fields['attributes'].widget = AttributesWidget()
