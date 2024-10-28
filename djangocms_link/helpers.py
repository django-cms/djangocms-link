from __future__ import annotations

from django.apps import apps
from django.contrib.sites.models import Site
from django.db import models


def get_manager(model: models.Model, current_content: bool = False) -> models.Manager:
    if hasattr(model, "admin_manager"):
        return model.admin_manager.current_content() if current_content else model.admin_manager
    return model.objects


def get_rel_obj(internal_link: str) -> models.Model | None:
    if ":" in internal_link:
        model, pk = internal_link.split(":", 1)
        model = apps.get_model(*model.split(".", 1))
        return get_manager(model).filter(pk=pk).first()
    return None


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
    else:
        return None

    if hasattr(obj, "get_absolute_url"):
        # Access site id if possible (no db access necessary)
        if site_id is None:
            site_id = Site.objects.get_current().id
        obj_site_id = getattr(obj, "site_id", getattr(getattr(obj, "node", None), "site_id", None))
        link_field_value["__cache__"] = obj.get_absolute_url()  # Can be None
        if obj_site_id and obj_site_id != site_id:
            ref_site = Site.objects._get_site_by_id(obj_site_id).domain
            link_field_value["__cache__"] = f"//{ref_site}{link_field_value['__cache__']}"
        if link_field_value["__cache__"]:
            link_field_value["__cache__"] += link_field_value.get("anchor", "")
    elif hasattr(obj, "url"):
        link_field_value["__cache__"] = obj.url
    else:
        link_field_value["__cache__"] = None
    return link_field_value["__cache__"]
