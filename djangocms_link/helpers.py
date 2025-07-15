from __future__ import annotations

from django.apps import apps
from django.contrib.sites.models import Site
from django.db import models


try:
    from filer.models import File
except (ModuleNotFoundError, ImportError):  # pragma: no cover
    File = None


def get_manager(model: models.Model, current_content: bool = False) -> models.Manager:
    if hasattr(model, "admin_manager"):
        return (
            model.admin_manager.current_content()
            if current_content
            else model.admin_manager
        )
    return model.objects


def get_rel_obj(internal_link: str) -> models.Model | None:
    if ":" in internal_link:
        model, pk = internal_link.split(":", 1)
        model = apps.get_model(*model.split(".", 1))
        return get_manager(model).filter(pk=pk).first()


def get_obj_link(obj: models.Model, site_id: int | None = None) -> str:
    # Access site id if possible (no db access necessary)
    if site_id is None:
        site_id = Site.objects.get_current().id
    obj_site_id = getattr(
        obj, "site_id", getattr(getattr(obj, "node", None), "site_id", None)
    )
    link = obj.get_absolute_url()  # Can be None
    if link and obj_site_id and obj_site_id != site_id:
        ref_site = Site.objects._get_site_by_id(obj_site_id).domain
        link = f"//{ref_site}{link}"
    return link


def get_link(link_field_value: dict, site_id: int | None = None) -> str | None:
    if not link_field_value:
        return None
    if "external_link" in link_field_value:
        if link_field_value["external_link"].startswith("tel:"):
            return link_field_value["external_link"].replace(" ", "")
        return link_field_value["external_link"] or None

    if "__cache__" in link_field_value:
        return link_field_value["__cache__"] or None

    if "internal_link" in link_field_value:
        obj = get_rel_obj(link_field_value["internal_link"])
    elif "file_link" in link_field_value:
        obj = get_rel_obj("filer.file:" + str(link_field_value["file_link"]))
    else:  # pragma: no cover
        return None

    if hasattr(obj, "get_absolute_url"):
        link_field_value["__cache__"] = get_obj_link(obj, site_id)  # Can be None
        if link_field_value["__cache__"]:
            link_field_value["__cache__"] += link_field_value.get("anchor", "")
    elif hasattr(obj, "url"):
        link_field_value["__cache__"] = obj.url
    else:
        link_field_value["__cache__"] = None
    return link_field_value["__cache__"]


class LinkDict(dict):
    """dict subclass with two additional properties: url and type to easily infer the link type and
    the url of the link. The url property is cached to avoid multiple db lookups."""

    def __init__(self, initial=None, **kwargs):
        anchor = kwargs.pop("anchor", None)
        super().__init__(**kwargs)
        if initial:
            if isinstance(initial, dict):
                self.update(initial)
            elif isinstance(initial, str):
                self["external_link"] = initial
            elif isinstance(initial, File):
                self["file_link"] = initial.pk
            elif isinstance(initial, models.Model):
                self["internal_link"] = (
                    f"{initial._meta.app_label}.{initial._meta.model_name}:{initial.pk}"
                )
                # Prepopulate cache since we have to object to get the URL
                self["__cache__"] = initial.get_absolute_url()
                if self["__cache__"] and anchor:
                    self["__cache__"] += anchor

    @property
    def url(self) -> str:
        return get_link(self) or ""

    @property
    def type(self) -> str:
        for key in ("internal_link", "file_link"):
            if key in self:
                return key
        if "external_link" in self:
            if self["external_link"].startswith("tel:"):
                return "tel"
            if self["external_link"].startswith("mailto:"):
                return "mailto"
            if self["external_link"].startswith("#"):
                return "anchor"
            return "external_link"
        return ""

    def __str__(self):
        """If inserted into a Django template, expand the url."""
        return self.url
