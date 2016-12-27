# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import ValidationError
from django.forms.models import ModelForm
from django.forms.widgets import Media
from django.utils.encoding import force_text
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

    class Meta:
        model = Link
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')

    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        self.fields['attributes'].widget = AttributesWidget()

    def clean(self):
        cleaned_data = super(LinkForm, self).clean()
        field_names = (
            'external_link',
            'internal_link',
            'mailto',
            'phone',
        )
        anchor_field_name = 'anchor'
        field_names_allowed_with_anchor = (
            'external_link',
            'internal_link',
        )

        anchor_field_verbose_name = force_text(
            getattr(self.fields.get(anchor_field_name), 'label'))
        anchor_field_value = cleaned_data.get(anchor_field_name)

        link_fields = {
            key: cleaned_data.get(key)
            for key in field_names
        }
        link_field_verbose_names = {
            key: force_text(getattr(self.fields.get(key), 'label'))
            for key in link_fields.keys()
        }
        provided_link_fields = {
            key: value
            for key, value in link_fields.items()
            if value
        }

        if len(provided_link_fields) > 1:
            # Too many fields have a value.
            error_msg = '{} {}'.format(
                _('Only one of these fields is allowed:'),
                ', '.join(link_field_verbose_names.values()),
            )
            errors = {}
            for field, value in link_fields.items():
                if value:
                    errors[field] = error_msg
            raise ValidationError(errors)

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
        return cleaned_data
