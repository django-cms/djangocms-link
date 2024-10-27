from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoCmsLinkConfig(AppConfig):
    name = "djangocms_link"
    verbose_name = _("django CMS Link")

    def ready(self):
        # Only scan admins after all apps are loaded

        from django.contrib import admin

        from djangocms_link import admin as link_admin

        if link_admin.REGISTERED_ADMIN == "auto":
            # Autoconfig? Check the admin registry for suitable admins
            link_admin.REGISTERED_ADMIN = []
            for _admin in admin.site._registry.values():
                if _admin.model._meta.app_label == "cms":
                    # Skip CMS models
                    continue
                # search_fields need to be defined in the ModelAdmin class, and the model needs to have
                # a get_absolute_url method.
                if getattr(_admin, "search_fields", []) and hasattr(_admin.model, "get_absolute_url"):
                    link_admin.REGISTERED_ADMIN.append(_admin)
