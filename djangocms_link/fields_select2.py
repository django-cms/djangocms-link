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
    def __init__(self, site=None, *args, **kwargs):
        self.site = site
        super(Select2PageSelectWidget, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return Page.objects.drafts().on_site(self.site) if self.site is not None else Page.objects.drafts()


class Select2PageSearchField(forms.ChoiceField):
    site = None
    widget = Select2PageSelectWidget(site=site)
