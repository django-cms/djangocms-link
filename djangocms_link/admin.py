from __future__ import annotations

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import F, Model, Prefetch, Q, QuerySet
from django.http import Http404, HttpRequest, JsonResponse
from django.urls import path
from django.utils.translation import gettext as _
from django.views.generic.list import BaseListView

from cms import __version__
from cms.models import Page
from cms.utils import get_language_from_request, get_language_list

from . import models
from .fields import LinkFormField, LinkWidget
from .helpers import get_manager


UNICODE_SPACE = "\u3000"  # This is a full-width space character (U+3000)


_version = int(__version__.split(".")[0])
if _version >= 4:
    from cms.admin.utils import GrouperModelAdmin
    from cms.models import PageContent
else:
    from cms.models import Title as PageContent

    class GrouperModelAdmin:
        pass


REGISTERED_ADMIN = []  # Will be set by djangocms_link.apps.DjangoCmsLinkConfig.ready


class AdminUrlsView(BaseListView):
    """Handle AutocompleteWidget's AJAX requests for data."""

    paginate_by = getattr(settings, "DJANGOCMS_LINK_PAGINATE_BY", 50)
    admin_site = None

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """
        Return a JsonResponse with search results (query parameter "q") usable by
        Django admin's autocomplete view. Each item is returned as defined in
        serialize_result(), for example:
        {
            "results": [
                {
                    "text": "Page",
                    "children" : [
                        {
                             "id": "cms.page:5",
                             "text": "My first page",
                             "url": "/en/my-first-page/",
                             "verbose_name": "Pages",
                         }, ...
                    ]
                 }, ...
             ],
             "pagination": {"more": true}
        }

        If the endpoint is called with the query parameter "g" (for get), the view will
        search for the id (e.g., "cms.page:5") and return its entry as defined in
        serialize_results(), e.g.:
        {
             "id": "cms.page:5",
             "text": "My first page",
             "url": "/en/my-first-page/",
             "verbose_name": "Pages",
         }
        """
        if request.GET.get("g"):
            # Get name of a reference
            return self.get_reference(request)

        self.term, self.language, self.site = self.process_request(request)

        if not self.has_perm(request):
            raise PermissionDenied

        qs_list = [self.get_queryset()]
        self.add_admin_querysets(qs_list)
        self.object_list = self.get_paginated_multi_qs(qs_list)
        context = self.get_context_data()
        results = self.get_optgroups(context)
        return JsonResponse(
            {
                "results": results,
                "pagination": {"more": context["page_obj"].has_next()},
            }
        )

    def get_page(self) -> int:
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            raise Http404(
                _("Page is not “last”, nor can it be converted to an int.")
            )
        return page_number

    def get_paginated_multi_qs(self, qs_list: list[QuerySet]) -> list[Model] | QuerySet:
        """
        Paginate multiple querysets and return a result list.
        """
        if len(qs_list) == 1:
            # Only one qs, just use regular pagination
            return qs_list[0]
        # Slize all querysets, evaluate and join them into a list
        max_items = self.get_page() * self.paginate_by
        objects = []
        for qs in qs_list:
            for item in qs:
                if self.has_perm(self.request, item):
                    objects.append(item)

            if len(objects) >= max_items:
                # No need to touch the rest of the querysets
                # as we have enough items already
                break
        return objects

    def get_reference(self, request: HttpRequest) -> JsonResponse:
        try:
            model_str, pk = request.GET.get("g").split(":")
            app, model = model_str.split(".")
            model = apps.get_model(app, model)
            model_admin = self.admin_site._registry.get(model)
            language = get_language_from_request(request)

            if model_str == "cms.page" and _version >= 4 or model_admin is None:
                obj = get_manager(model).get(pk=pk)
                if model_str == "cms.page":
                    obj.__link_text__ = obj.get_admin_content(language, fallback=True).title
                return JsonResponse(self.serialize_result(obj))
            elif model_str == "cms.page":
                obj = get_manager(model).get(pk=pk)
                obj.__link_text__ = obj.get_title(language, fallback=True)
                return JsonResponse(self.serialize_result(obj))

            if hasattr(model_admin, "get_link_queryset"):
                obj = model_admin.get_link_queryset(self.request, None).get(pk=pk)
            else:
                obj = model_admin.get_queryset(self.request).get(pk=pk)
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
        if model:
            results.append(model)
        return results

    def serialize_result(self, obj: Model) -> dict:
        """
        Convert the provided model object to a dictionary that is added to the
        results list.
        """
        if isinstance(obj, Page) and hasattr(obj, "prefetched_content") and hasattr(obj, "get_admin_content"):
            obj.admin_content_cache = {trans.language: trans for trans in obj.prefetched_content}
            obj.__link_text__ = obj.get_admin_content(self.language).title

        indentation = UNICODE_SPACE * (max(getattr(obj, "__depth__", 1), 1) - 1)
        return {
            "id": f"{obj._meta.app_label}.{obj._meta.model_name}:{obj.pk}",
            "text": indentation + (getattr(obj, "__link_text__", str(obj)) or str(obj)),
            "url": obj.get_absolute_url(),
            "verbose_name": str(obj._meta.verbose_name).capitalize(),
        }

    def get_queryset(self) -> QuerySet:
        """Return queryset based on ModelAdmin.get_search_results()."""
        languages = get_language_list()
        try:
            # django CMS 4.1/5.0+
            content_qs = (
                PageContent.admin_manager.filter(language__in=languages)
                .filter(
                    Q(title__icontains=self.term) | Q(menu_title__icontains=self.term)
                )
                .current_content()
            )
            qs = (
                Page.objects.filter(pk__in=content_qs.values_list("page_id", flat=True))
                .order_by("path" if _version >= 5 else "node__path")
                .prefetch_related(
                    Prefetch(
                        "pagecontent_set",
                        to_attr="prefetched_content",
                        queryset=PageContent.admin_manager.current_content(),
                    ),
                )
            )
            if not self.term:
                qs = qs.annotate(
                    __depth__=F("depth" if _version >= 5 else "node__depth")
                )
            if self.site:
                qs = qs.filter(site_id=self.site) if _version >= 5 else qs.filter(node__site_id=self.site)
        except (AttributeError,):
            # django CMS 3.11
            qs = (
                get_manager(PageContent, current_content=True)
                .filter(language__in=languages)
                .filter(
                    Q(title__icontains=self.term) | Q(menu_title__icontains=self.term)
                )
            )
            qs = (
                Page.objects.filter(pk__in=qs.values_list("page_id", flat=True))
                .order_by("node__path")
                .prefetch_related(
                    Prefetch(
                        "title_set",
                        to_attr="prefetched_content",
                        queryset=get_manager(PageContent, current_content=True).all(),
                    ),
                )
            )
            if "publisher_draft" in Page._meta.fields_map:
                # django CMS 3.11
                qs = qs.filter(publisher_is_draft=True)
            if not self.term:
                qs = qs.annotate(
                    __depth__=F("node__depth")
                )

            if self.site:
                qs = qs.filter(node__site_id=self.site)
        return qs

    def add_admin_querysets(self, qs: list[QuerySet]) -> None:
        for model_admin in REGISTERED_ADMIN:
            try:
                # hack: GrouperModelAdmin expects a language to be temporarily set
                if isinstance(model_admin, GrouperModelAdmin):  # pragma: no cover
                    model_admin.language = self.language
                if hasattr(model_admin, "get_link_queryset"):
                    # Allow model admins to define get_link_queryset to do additional
                    # filtering, sorting and potentially custom site selection
                    new_qs = model_admin.get_link_queryset(self.request, self.site)
                else:
                    new_qs = model_admin.get_queryset(self.request)
                    if hasattr(model_admin.model, "site") and self.site:
                        new_qs = new_qs.filter(
                            Q(site_id=self.site) | Q(site__isnull=True)
                        )
                    elif hasattr(model_admin.model, "sites") and self.site:
                        new_qs = new_qs.filter(sites__id=self.site)
                new_qs, search_use_distinct = model_admin.get_search_results(self.request, new_qs, self.term)
                if search_use_distinct:  # pragma: no cover
                    new_qs = new_qs.distinct()
                qs.append(new_qs)
            except Exception:  # pragma: no cover
                # Still report back remaining urls even if one model fails
                pass

        return qs

    def process_request(self, request: HttpRequest) -> tuple[str, str, int | None]:
        """
        Validate request integrity, extract and return request parameters.
        """
        term = request.GET.get("term", request.GET.get("q", "")).strip("  ").lower()
        site = request.GET.get(
            "app_label", ""
        )  # Django admin's app_label is abused as site id
        try:
            site = int(site)
        except ValueError:
            site = None
        language = get_language_from_request(request)
        return term, language, site

    def has_perm(self, request: HttpRequest, obj=None) -> bool:
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

    global_link_form_widget = LinkWidget
    global_link_form_field = LinkFormField
    global_link_url_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.global_link_url_name = f"{self.opts.app_label}_{self.opts.model_name}_urls"

    def has_module_permission(self, request: HttpRequest) -> bool:  # pragma: no cover
        # Remove from admin
        return False

    def get_urls(self) -> list:
        # Only url endpoint public, do not call super().get_urls()
        return [
            path(
                "urls",
                self.admin_site.admin_view(self.url_view),
                name=self.global_link_url_name,
            ),
        ]

    def url_view(self, request: HttpRequest) -> JsonResponse:
        return AdminUrlsView.as_view(admin_site=self.admin_site)(request)


admin.site.register(models.Link, LinkAdmin)
