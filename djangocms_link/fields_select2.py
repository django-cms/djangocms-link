from django import forms

from cms.models import Page

from django_select2.forms import ModelSelect2Widget

from djangocms_link.helpers import get_queryset_manager


class Select2PageSearchFieldMixin:
    search_fields = [
        'title_set__title__icontains',
        'title_set__menu_title__icontains',
        'title_set__slug__icontains'
    ]

    def label_from_instance(self, obj):
        return obj.get_title()


class Select2PageSelectWidget(Select2PageSearchFieldMixin, ModelSelect2Widget):
    site = None

    # show entries when clicking on it
    def build_attrs(self, base_attrs, extra_attrs=None):
        default_attrs = {"data-minimum-input-length": 0}
        default_attrs.update(base_attrs)
        attrs = super().build_attrs(default_attrs, extra_attrs=extra_attrs)
        return attrs

    def get_queryset(self):
        # django CMS < 4
        base_queryset = get_queryset_manager(Page.objects)
        if self.site:
            return base_queryset.on_site(self.site)
        return base_queryset.all()

    # we need to implement jQuery ourselves, see #180
    class Media:
        js = (
            "https://code.jquery.com/jquery-3.5.1.slim.min.js",
        )


class Select2PageSearchField(forms.ModelChoiceField):
    widget = Select2PageSelectWidget()

    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = self.widget.get_queryset()
        super().__init__(*args, **kwargs)
