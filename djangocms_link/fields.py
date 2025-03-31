from __future__ import annotations

import json

from django.apps import apps
from django.conf import settings
from django.contrib.admin import site
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS, AutocompleteSelect
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import JSONField, ManyToOneRel
from django.forms import Field, MultiWidget, Select, TextInput, URLInput
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from cms.utils.urlutils import admin_reverse

from djangocms_link.helpers import LinkDict, get_manager


try:
    from filer.fields.file import AdminFileWidget, FilerFileField
    from filer.models import File
except (ModuleNotFoundError, ImportError):  # pragma: no cover
    File = None

from djangocms_link.validators import AnchorValidator, ExtendedURLValidator


MINIMUM_INPUT_LENGTH = getattr(settings, "DJANGOCMS_LINK_MINIMUM_INPUT_LENGTH", 0)


class LinkAutoCompleteWidget(AutocompleteSelect):
    def __init__(self, attrs: dict | None = None):
        super().__init__(None, None, attrs)

    def get_internal_obj(self, values: list[str | None]) -> list[models.Model | None]:
        internal_obj = []
        for value in values:
            if value:
                model_path, pk = value.split(":", 1)
                model = apps.get_model(*model_path.split(".", 1))
                internal_obj.append(get_manager(model).filter(pk=pk).first())
            else:
                internal_obj.append(None)
        return internal_obj

    def optgroups(self, name: str, value: str, attr: str | None = None):
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

    def build_attrs(self, base_attrs: dict, extra_attrs: dict | None = None) -> dict:
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
                "data-minimum-input-length": MINIMUM_INPUT_LENGTH,
                "lang": i18n_name,
                "class": attrs["class"]
                + (" " if attrs["class"] else "")
                + "admin-autocomplete",
            }
        )
        return attrs


class SiteAutocompleteSelect(AutocompleteSelect):
    no_sites = None

    def __init__(self, attrs: dict | None = None):
        # Hack: Pretend that the user is selecting a site for a Page object
        # and use Django admin's autocomplete widget
        try:
            from cms.models.pagemodel import TreeNode

            field = TreeNode._meta.get_field("site")
        except ImportError:  # pragma: no cover
            # django CMS 4.2+
            from cms.models import Page

            field = Page._meta.get_field("site")
        super().__init__(field, site, attrs)

    def optgroups(self, name: str, value: str, attr: dict | None = None):
        default = (None, [], 0)
        groups = [default]
        has_selected = False
        selected_choices = set(value)
        default[1].append(self.create_option(name, "", "", False, 0))

        site = Site.objects.get_current()
        option_value, option_label = site.pk, str(site)

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


# Configure the LinkWidget
link_types = {
    "internal_link": _("Internal link"),
    "external_link": _("External link/anchor"),
}
if File:
    link_types["file_link"] = _("File link")

# Get the allowed link types from the settings
allowed_link_types = getattr(
    settings,
    "DJANGOCMS_LINK_ALLOWED_LINK_TYPES",
    ("internal_link", "external_link", "file_link", "anchor", "mailto", "tel"),
)

# Adjust example uri schemes to allowed link types
example_uri_scheme = (
    "'https://'"
    + (", 'tel:'" if "tel" in allowed_link_types else "")
    + (", or 'mailto:'" if "mailto" in allowed_link_types else "")
)

# Show anchor sub-widget only for internal_link
_mapping = {key: key for key in link_types.keys()}
_mapping["anchor"] = "internal_link"

# Remove disallowed link types
link_types = {
    key: value for key, value in link_types.items() if key in allowed_link_types
}

# Create the available widgets
_available_widgets = {
    "always": Select(
        choices=list(link_types.items()),
        attrs={
            "class": "js-link-widget-selector",
            "data-help": _(
                "No destination selected. Use the dropdown to select a destination."
            ),
        },
    ),  # Link type selector
    "external_link": URLInput(
        attrs={
            "widget": "external_link",
            "placeholder": _("https://example.com or #anchor"),
            "data-help": _(
                "Provide a link to an external URL, including the schema such as {}. "
                "Optionally, add an #anchor (including the #) to scroll to."
            ).format(example_uri_scheme),
        },
    ),  # External link input
    "internal_link": LinkAutoCompleteWidget(
        attrs={
            "widget": "internal_link",
            "data-help": _(
                "Select from available internal destinations. Optionally, add an anchor to scroll to."
            ),
            "data-placeholder": _("Select internal destination"),
        },
    ),  # Internal link selector
    "anchor": TextInput(
        attrs={
            "widget": "anchor",
            "placeholder": _("#anchor"),
            "data-help": _("Provide an anchor to scroll to."),
        }
    ),
}
if File:
    _available_widgets["file_link"] = AdminFileWidget(
        rel=ManyToOneRel(FilerFileField, File, "id"),
        admin_site=site,
        attrs={
            "widget": "file_link",
            "data-help": _("Select a file as destination."),
        },
    )


class LinkWidget(MultiWidget):
    template_name = "djangocms_link/admin/link_widget.html"
    data_pos = {}
    number_sites = None
    default_site_selector = getattr(settings, "DJANGOCMS_LINK_SITE_SELECTOR", False)

    class Media:
        js = ("djangocms_link/link-widget.js",)
        css = {"all": ("djangocms_link/link-widget.css",)}

    def __init__(self, site_selector: bool | None = None):
        if site_selector is None:
            site_selector = LinkWidget.default_site_selector

        widgets = [
            widget
            for key, widget in _available_widgets.items()
            if key == "always" or _mapping[key] in link_types
        ]
        if site_selector and "internal_link" in allowed_link_types:
            index = next(
                i
                for i, widget in enumerate(widgets)
                if widget.attrs.get("widget") == "internal_link"
            )
            widgets.insert(
                index,
                SiteAutocompleteSelect(
                    attrs={
                        "class": "js-link-site-widget",
                        "widget": "site",
                        "data-placeholder": _("Select site"),
                    },
                ),
            )  # Site selector

        # Remember which widget expets its content at which position
        self.data_pos = {
            widget.attrs.get("widget"): i for i, widget in enumerate(widgets)
        }
        super().__init__(widgets)

    def get_context(self, name: str, value: str | None, attrs: dict) -> dict:
        if not self.is_required:
            self.widgets[0].choices = [("empty", "---------")] + self.widgets[0].choices
        context = super().get_context(name, value, attrs)
        context["widget"]["subwidgets"] = {
            widget["attrs"].get("widget", "link-type-selector"): widget
            for widget in context["widget"]["subwidgets"]
        }
        if File and "file_link" in allowed_link_types:
            del context["widget"]["subwidgets"]["file_link"]
            index = next(
                i
                for i, widget in enumerate(self.widgets)
                if widget.attrs.get("widget") == "file_link"
            )
            context["filer_widget"] = self.widgets[index].render(
                name + f"_{index}", value[index], attrs
            )
        return context


class LinkFormField(Field):
    widget = LinkWidget
    external_link_validators = [
        ExtendedURLValidator(allowed_link_types=allowed_link_types)
    ]
    internal_link_validators = []
    file_link_validators = []
    anchor_validators = [AnchorValidator()]

    empty_values = [None, {}]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("help_text", _("Select a link type and provide a link."))
        kwargs.setdefault("initial", {})
        kwargs.pop("encoder", None)  # Passed from LinkField's JSONField parent class
        kwargs.pop("decoder", None)  # but not needed
        super().__init__(*args, **kwargs)
        if isinstance(self.initial, dict):
            self.initial = self.prepare_value(self.initial)

    def prepare_value(self, value: dict) -> list[str | None]:
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

    def to_python(self, value: list[str | None]) -> dict:
        """Turn MultiWidget list data into LinkField dict format"""
        if not value:
            return LinkDict()

        link_type = value[0]
        pos = self._get_pos(link_type)
        if not pos or not value[pos]:  # No link type selected or no value
            return LinkDict()
        pos_anchor = self._get_pos("anchor")

        python = LinkDict({link_type: value[pos]} if value[pos] else {})
        if python and link_type == "internal_link" and pos_anchor and value[pos_anchor]:
            python["anchor"] = value[pos_anchor]
        return python

    def run_validators(self, value: LinkDict):
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
        kwargs.setdefault("default", dict)
        kwargs.setdefault("help_text", "-")  # Help text is set by the widget
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", LinkFormField)
        return super().formfield(**kwargs)

    def get_prep_value(self, value):
        if isinstance(value, dict):
            # Drop any cached value without changing the original value
            return super().get_prep_value(dict(**{
                key: val for key, val in value.items() if key != "__cache__"
            }))
        return super().get_prep_value(value)

    def from_db_value(self, value, expression, connection):
        value = super().from_db_value(value, expression, connection)
        return LinkDict(value)

    def to_python(self, value):
        value = super().to_python(value)
        return LinkDict(value)
