import json

from django.apps import apps
from django.conf import settings
from django.contrib.admin import site
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS, AutocompleteSelect
from django.db.models import JSONField, ManyToOneRel
from django.forms import Field, MultiWidget, Select, TextInput, URLInput
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from cms.utils.urlutils import admin_reverse


try:
    from filer.fields.file import AdminFileWidget, FilerFileField
    from filer.models import File
except (ModuleNotFoundError, ImportError):
    File = None

from djangocms_link.validators import AnchorValidator, ExtendedURLValidator


link_types = {
    "internal_link": _("Internal link"),
    "external_link": _("External link/anchor"),
}
if File:
    link_types["file_link"] = _("File link")


MINIMUM_INPUT_LENGTH = getattr(
    settings, "DJANGOCMS_LINK_SELECT2_MINIMUM_INPUT_LENGTH", 0
)


class LinkAutoCompleteWidget(AutocompleteSelect):
    def get_internal_obj(self, values):
        internal_obj = []
        for value in values:
            if value:
                model_path, pk = value.split(":", 1)
                model = apps.get_model(*model_path.split(".", 1))
                if hasattr(model, "admin_manager"):
                    internal_obj.append(model.admin_manager.filter(pk=pk).first())
                else:
                    internal_obj.append(model.objects.filter(pk=pk).first())
            else:
                internal_obj.append(None)
        return internal_obj

    def optgroups(self, name, value, attr=None):
        default = (None, [], 0)
        groups = [default]
        has_selected = False
        selected_choices = set(value)
        if not self.is_required and not self.allow_multiple_selected:
            default[1].append(self.create_option(name, "", "", False, 0))

        for option_value, option_label in zip(value, self.get_internal_obj(value)):
            selected = str(option_value) in value and (
                has_selected is False or self.allow_multiple_selected
            )
            has_selected |= selected
            index = len(default[1])
            subgroup = default[1]
            subgroup.append(
                self.create_option(
                    name, option_value, option_label, selected_choices, index
                )
            )
        return groups

    def get_url(self):
        return admin_reverse("djangocms_link_link_urls")

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set select2's AJAX attributes.

        Attributes can be set using the html5 data attribute.
        Nested attributes require a double dash as per
        https://select2.org/configuration/data-attributes#nested-subkey-options
        """
        attrs = super(Select, self).build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault("class", "")
        i18n_name = getattr(
            self, "i18n_name", SELECT2_TRANSLATIONS.get(get_language())
        )  # Django 3.2 compat
        attrs.update(
            {
                "data-ajax--cache": "true",
                "data-ajax--delay": 250,
                "data-ajax--type": "GET",
                "data-ajax--url": self.get_url(),
                "data-theme": "admin-autocomplete",
                "data-allow-clear": json.dumps(not self.is_required),
                "data-placeholder": "",  # Allows clearing of the input.
                "lang": i18n_name,
                "class": attrs["class"]
                + (" " if attrs["class"] else "")
                + "admin-autocomplete",
            }
        )
        return attrs


class LinkWidget(MultiWidget):
    template_name = "djangocms_link/admin/link_widget.html"
    data_pos = {}

    class Media:
        js = ("djangocms_link/link-widget.js",)
        css = {"all": ("djangocms_link/link-widget.css",)}

    def __init__(self):
        widgets = [
            Select(
                choices=list(link_types.items()),
                attrs={
                    "class": "js-link-widget-selector",
                    "data-help": _("No destination selected. Use the dropdown to select a destination.")
                },
            ),  # Link type selector
            LinkAutoCompleteWidget(
                field=None,
                admin_site=None,
                attrs={
                    "widget": "internal_link",
                    "data-help": _(
                        "Select from available internal destinations. Optionally, add an anchor to scroll to."
                    ),
                },
            ),  # Internal link selector
            URLInput(
                attrs={
                    "widget": "external_link",
                    "placeholder": _("https://example.com or #anchor"),
                    "data-help": _(
                        "Provide a link to an external URL, including the schema such as 'https://', 'tel:', "
                        "or 'mailto:'. Optionally, add an #anchor (including the #) to scroll to."
                    ),
                },
            ),  # External link input
            TextInput(
                attrs={
                    "widget": "anchor",
                    "placeholder": _("#anchor"),
                    "data-help": _("Provide an anchor to scroll to."),
                }
            ),
        ]
        if File:
            widgets.append(
                AdminFileWidget(
                    rel=ManyToOneRel(FilerFileField, File, "id"),
                    admin_site=site,
                    attrs={
                        "widget": "file_link",
                        "data-help": _("Select a file as destination."),
                    },
                ),
            )
        # Remember which widget expets its content at which position
        self.data_pos = {
            widget.attrs.get("widget"): i for i, widget in enumerate(widgets)
        }
        super().__init__(widgets)

    def get_context(self, name, value, attrs):
        if not self.is_required:
            self.widgets[0].choices = [("empty", "---------")] + self.widgets[0].choices
        context = super().get_context(name, value, attrs)
        context["widget"]["subwidgets"] = {
            widget["attrs"].get("widget", "link-type-selector"): widget
            for widget in context["widget"]["subwidgets"]
        }
        if File:
            del context["widget"]["subwidgets"]["file_link"]
            context["filer_widget"] = self.widgets[-1].render(name + "_4", value[4], attrs)
        return context


class LinkFormField(Field):
    widget = LinkWidget
    external_link_validators = [ExtendedURLValidator()]
    internal_link_validators = []
    file_link_validators = []
    anchor_validators = [AnchorValidator()]

    empty_values = [{}] + [{link_type: ""} for link_type in link_types]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("help_text", _("Select a link type and provide a link."))
        kwargs.pop("encoder", None)  # Passed from LinkField's JSONField parent class
        kwargs.pop("decoder", None)  # but not needed
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        if isinstance(value, list):
            return value

        multi_value = len(self.widget.widgets) * [None]
        if "external_link" in value:
            pos = self._get_pos("external_link")
            multi_value[0] = "external_link"
            multi_value[pos] = value["external_link"]
        elif "internal_link" in value:
            pos = self._get_pos("internal_link")
            anchor_pos = self._get_pos("anchor")
            multi_value[0] = "internal_link"
            multi_value[pos] = value["internal_link"]
            multi_value[anchor_pos] = value.get("anchor", "")
        elif "file_link" in value:
            multi_value[0] = "file_link"
            pos = self._get_pos("file_link")
            multi_value[pos] = str(value["file_link"])
        return multi_value

    def to_python(self, value):
        """Turn MultiWidget list data into LinkField dict format"""
        if not value:
            return {}

        link_type = value[0]
        pos = self._get_pos(link_type)
        if not pos:  # No link type selected
            return {}
        pos_anchor = self._get_pos("anchor")

        python = {link_type: value[pos]}
        if link_type == "internal_link" and pos_anchor and value[pos_anchor]:
            python["anchor"] = value[pos_anchor]
        return python

    def run_validators(self, value):
        """Check for <link_type>_validators property and run the validators"""
        for link_type in link_types:
            if link_type in value:
                self.validators = getattr(self, f"{link_type}_validators", [])
                super().run_validators(value[link_type])
        if "anchor" in value:
            self.validators = getattr(self, "anchor_validators", [])
            super().run_validators(value["anchor"])

    def _get_pos(self, link_type):
        """Returns the position of the different link type widgets"""
        return self.widget.data_pos.get(link_type)


class LinkField(JSONField):
    """A link is a JSON field with a default LinkFormField"""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", {})
        kwargs.setdefault("blank", True)
        kwargs.setdefault("help_text", "-")
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", LinkFormField)
        return super().formfield(**kwargs)
