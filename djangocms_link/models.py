"""
Enables the user to add a "Link" plugin that displays a link
using the HTML <a> tag.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_str
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from cms.models import CMSPlugin

from djangocms_attributes_field.fields import AttributesField

from .fields import LinkField
from .helpers import get_link
from .validators import IntranetURLValidator


# Add additional choices through the ``settings.py``.
def get_templates():
    choices = [
        ("default", _("Default")),
    ]
    choices += getattr(
        settings,
        "DJANGOCMS_LINK_TEMPLATES",
        [],
    )
    return choices


HOSTNAME = getattr(settings, "DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN", None)

TARGET_CHOICES = (
    ("_blank", _("Open in new window")),
    ("_self", _("Open in same window")),
    ("_parent", _("Delegate to parent")),
    ("_top", _("Delegate to top")),
)


class AbstractLink(CMSPlugin):
    # used by django CMS search
    search_fields = ("name",)

    # allows link requirement to be changed when another
    # CMS plugin inherits from AbstractLink
    link_is_optional = False

    url_validators = [
        IntranetURLValidator(intranet_host_re=HOSTNAME),
    ]

    template = models.CharField(
        verbose_name=_("Template"),
        choices=get_templates(),
        default=get_templates()[0][0],
        max_length=255,
    )
    name = models.CharField(
        verbose_name=_("Display name"),
        blank=True,
        max_length=255,
    )

    link = LinkField(
        verbose_name=_("Link"),
    )
    # advanced options
    target = models.CharField(
        verbose_name=_("Target"),
        choices=TARGET_CHOICES,
        blank=True,
        max_length=255,
    )
    attributes = AttributesField(
        verbose_name=_("Attributes"),
        blank=True,
        excluded_keys=["href", "target"],
    )

    # Add an app namespace to related_name to avoid field name clashes
    # with any other plugins that have a field with the same name as the
    # lowercase of the class name of this model.
    # https://github.com/divio/django-cms/issues/5030
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin,
        related_name="%(app_label)s_%(class)s",
        parent_link=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name or str(self.pk)

    def get_short_description(self):
        link = self.get_link()
        if self.name and link:
            return f"{self.name} ({link})"
        return self.name or link or gettext("<link is missing>")

    def get_link(self, site_id=None):
        return get_link(self.link, site_id)

    def clean(self):
        super().clean()
        if not self.link_is_optional and not self.link:
            raise ValidationError(
                force_str(_("Link is required.")),
                code="required",
            )

    def __init__(self, *args, **wkargs):
        super().__init__(*args, **wkargs)
        self._meta.get_field("link").blank = self.link_is_optional


class Link(AbstractLink):
    class Meta:
        abstract = False
