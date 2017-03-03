from cms.models import Page
from django import forms

from django_select2.forms import ModelSelect2Widget


class Select2PageSearchFieldMixin(object):
    search_fields = [
        'title_set__title__icontains',
        'title_set__menu_title__icontains',
        'title_set__slug__icontains'
    ]


class Select2PageSelectWidget(Select2PageSearchFieldMixin, ModelSelect2Widget):
    site = None

    def get_queryset(self):
        if self.site:
            return Page.objects.drafts().on_site(self.site)
        return Page.objects.drafts()


class Select2PageSearchField(forms.ModelChoiceField):
    widget = Select2PageSelectWidget()

    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = self.widget.get_queryset()
        super(Select2PageSearchField, self).__init__(*args, **kwargs)
