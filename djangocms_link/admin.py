from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import FieldError, PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.urls import path
from django.views.generic.list import BaseListView

from cms import __version__
from cms.models import Page
from cms.utils import get_language_from_request

from . import models
from .helpers import get_manager


_version = int(__version__.split(".")[0])
if _version >= 4:
    from cms.admin.utils import GrouperModelAdmin
    from cms.models import PageContent
else:
    from cms.models import Title as PageContent

    class GrouperModelAdmin:
        pass

REGISTERED_ADMIN = getattr(settings, "DJANGOCMS_LINKABLE_MODELS", "auto")


class AdminUrlsView(BaseListView):
    """Handle AutocompleteWidget's AJAX requests for data."""

    paginate_by = 20
    admin_site = None

    def get(self, request, *args, **kwargs):
        """
        Return a JsonResponse with search results as defined in
        serialize_result(), by default:
        {
            results: [{id: "123" text: "foo"}],
            pagination: {more: true}
        }
        """
        if request.GET.get("g"):
            # Get name of a reference
            return self.get_reference(request)

        self.term, self.language, self.site = self.process_request(request)

        if not self.has_perm(request):
            raise PermissionDenied

        self.object_list = self.get_queryset()
        self.add_admin_querysets(self.object_list)
        context = self.get_context_data()
        results = self.get_optgroups(context)
        return JsonResponse(
            {
                "results": results,
                "pagination": {"more": context["page_obj"].has_next()},
            }
        )

    def get_reference(self, request):
        try:
            model, pk = request.GET.get("g").split(":")
            app, model = model.split(".")
            model = apps.get_model(app, model)
            obj = get_manager(model).get(pk=pk)
            return JsonResponse(self.serialize_result(obj))
        except Exception as e:
            return JsonResponse({"error": str(e)})

    def get_optgroups(self, context):
        results = []
        model = {}
        previous_model = None
        for obj in context["object_list"]:
            if obj._meta.verbose_name_plural != previous_model or not model:
                if model:  # Don't add the initial empty model
                    results.append(model)
                previous_model = obj._meta.verbose_name_plural
                model = {
                    "text": previous_model.capitalize(),
                    "children": [],
                }
            model["children"].append(self.serialize_result(obj))
        results.append(model)
        return results

    def serialize_result(self, obj):
        """
        Convert the provided model object to a dictionary that is added to the
        results list.
        """
        return {
            "id": f"{obj._meta.app_label}.{obj._meta.model_name}:{obj.pk}",
            "text": str(obj),
            "url": obj.get_absolute_url()
        }

    def get_queryset(self):
        """Return queryset based on ModelAdmin.get_search_results()."""
        try:
            # django CMS 4.2+
            qs = PageContent.admin_manager.filter(
                language=self.language, title__icontains=self.term
            ).current_content().values_list("page_id", flat=True)
            qs = Page.objects.filter(pk__in=qs).order_by("path")
            if self.site:
                qs = qs.filter(site_id=self.site)
        except (AttributeError, FieldError):
            # django CMS 3.11 - 4.1
            qs = get_manager(PageContent, current_content=True).filter(
                    language=self.language, title__icontains=self.term
                ).values_list("page_id", flat=True)
            qs = Page.objects.filter(pk__in=qs).order_by("node__path")
            if self.site:
                qs = qs.filter(node__site_id=self.site)
        return list(qs)

    def add_admin_querysets(self, qs):
        for model_admin in REGISTERED_ADMIN:
            try:
                # hack: GrouperModelAdmin expects a language to be temporarily set
                if isinstance(model_admin, GrouperModelAdmin):  # pragma: no cover
                    model_admin.language = self.language
                new_qs = model_admin.get_queryset(self.request)
                if hasattr(model_admin.model, "site") and self.site:
                    new_qs = new_qs.filter(Q(site_id=self.site) | Q(site__isnull=True))
                elif hasattr(model_admin.model, "sites") and self.site:
                    new_qs = new_qs.filter(sites__id=self.site)
                new_qs, search_use_distinct = model_admin.get_search_results(
                    self.request, new_qs, self.term
                )
                if search_use_distinct:  # pragma: no cover
                    new_qs = new_qs.distinct()

                qs += list(new_qs)
            except Exception:  # pragma: no cover
                # Still report back remaining urls even if one model fails
                pass

        return qs

    def process_request(self, request):
        """
        Validate request integrity, extract and return request parameters.
        """
        term = request.GET.get("term", "").strip("  ").lower()
        site = request.GET.get("app_label", "")  # Django admin's app_label is abused as site id
        try:
            site = int(site)
        except ValueError:
            site = None
        language = get_language_from_request(request)
        return term, language, site

    def has_perm(self, request, obj=None):
        """Check if user has permission to access the related model."""
        if obj is None:
            return True
        model_admin = self.admin_site._registry.get(obj.__class__)
        if model_admin is None:
            return False
        return model_admin.has_view_permission(request, obj=obj)


class LinkAdmin(admin.ModelAdmin):
    """The LinkAdmin class provides the endpoint for getting the urls. It is not visible in the
    admin interface."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.link_url_name = f"{self.opts.app_label}_{self.opts.model_name}_urls"

    def has_module_permission(self, request):  # pragma: no cover
        # Remove from admin
        return False

    def get_urls(self):
        # Only url endpoint public, do not call super().get_urls()
        return [
            path("urls",
                 self.admin_site.admin_view(self.url_view),
                 name=self.link_url_name
                 ),
        ]

    def url_view(self, request):
        return AdminUrlsView.as_view(admin_site=self)(request)


admin.site.register(models.Link, LinkAdmin)
