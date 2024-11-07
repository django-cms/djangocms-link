from django.apps import AppConfig, apps
from django.conf import settings
from django.contrib.admin import ModelAdmin
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


class DjangoCmsLinkConfig(AppConfig):
    name = "djangocms_link"
    verbose_name = _("django CMS Link")

    def ready(self):
        # Only scan admins after all apps are loaded
        from django.contrib import admin

        from djangocms_link import admin as link_admin

        linkable_models = getattr(settings, "DJANGOCMS_LINKABLE_MODELS", "auto")

        if linkable_models == "auto":  # pragma: no cover
            # Autoconfig? Check the admin registry for suitable admins
            link_admin.REGISTERED_ADMIN = []
            for _admin in admin.site._registry.values():
                if _admin.model._meta.app_label == "cms":
                    # Skip CMS models
                    continue
                # search_fields need to be defined in the ModelAdmin class, and the model needs to have
                # a get_absolute_url method.
                if getattr(_admin, "search_fields", []) and hasattr(
                    _admin.model, "get_absolute_url"
                ):
                    link_admin.REGISTERED_ADMIN.append(_admin)
        else:
            # turn model config into model admin instances
            admins = []
            for model in linkable_models:
                if isinstance(model, str):
                    model = apps.get_model(model)
                    if not hasattr(model, "get_absolute_url"):  # pragma: no cover
                        raise ImproperlyConfigured(
                            f"{model.__name__} needs to implement get_absolute_url method"
                        )
                    admin = admin.site._registry[model]
                    if admin not in admins:
                        admins.append(admin)
                elif not isinstance(model, ModelAdmin):  # pragma: no cover
                    raise ImproperlyConfigured(
                        'DJANGOCMS_LINK_LINKABLE_MODELS must be a list of string "app_label.model_name"'
                    )
            link_admin.REGISTERED_ADMIN = admins
