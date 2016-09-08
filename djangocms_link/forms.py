# -*- coding: utf-8 -*-
from django.forms import ValidationError
from django.forms.models import ModelForm
from django.forms.widgets import Media
from django.utils.translation import ugettext_lazy as _

from djangocms_attributes_field.widgets import AttributesWidget

from .models import Link


class LinkForm(ModelForm):
    try:
        from djangocms_link.fields import PageSearchField
        internal_link = PageSearchField(label=_('Page'), required=False)
    except ImportError:
        from cms.forms.fields import PageSelectFormField
        internal_link = PageSelectFormField(label=_('Page'), required=False)

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

    class Meta:
        model = Link
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')

    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        self.fields['attributes'].widget = AttributesWidget()

    def clean(self):
        cleaned_data = super(LinkForm, self).clean()
        external_link = cleaned_data.get('external_link')
        internal_link = cleaned_data.get('internal_link')
        mailto = cleaned_data.get('mailto')
        phone = cleaned_data.get('phone')
        anchor = cleaned_data.get('anchor')
        if not any([external_link, internal_link, mailto, phone, anchor]):
            raise ValidationError(_('At least one link is required.'))
        return cleaned_data

    # def _get_media(self):
    #     """
    #     Provide a description of all media required to render the widgets on this form
    #     """
    #     media = Media()
    #     for field in self.fields.values():
    #         media = media + field.widget.media
    #     media._js = ['cms/js/libs/jquery.min.js'] + media._js
    #     return media
    # media = property(_get_media)
