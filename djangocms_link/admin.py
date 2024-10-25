from django.apps import apps
from django.contrib import admin
from django.core.exceptions import FieldError, PermissionDenied
from django.http import JsonResponse
from django.urls import path
from django.views.generic.list import BaseListView

from cms import __version__
from cms.models import Page
from cms.utils import get_language_from_request

from . import models


_version = int(__version__.split(".")[0])
if _version >= 4:
    from cms.models import PageContent
else:
    from cms.models import Title as PageContent


class UrlsJsonView(BaseListView):
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

        self.term, self.language = self.process_request(request)

        if not self.has_perm(request):
            raise PermissionDenied

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse(
            {
                "results": [
                    {
                        "text": ("Pages"),
                        "children": [
                            self.serialize_result(obj) for obj in context["object_list"]
                        ],
                    },
                ],
                "pagination": {"more": context["page_obj"].has_next()},
            }
        )

    def get_reference(self, request):
        try:
            model, pk = request.GET.get("g").split(":")
            app, model = model.split(".")
            model = apps.get_model(app, model)
            if hasattr(model, "admin_manager"):
                obj = model.admin_manager.get(pk=pk)
            else:
                obj = model.objects.get(pk=pk)
            if isinstance(obj, Page) and _version >= 4:
                obj = obj.pagecontent_set(manager="admin_manager").current_content().first()
                return JsonResponse(self.serialize_result(obj))
            return JsonResponse(self.serialize_result(obj))
        except Exception as e:
            return JsonResponse({"error": str(e)})

    def serialize_result(self, obj):
        """
        Convert the provided model object to a dictionary that is added to the
        results list.
        """
        return {"id": f"cms.page:{obj.page.pk}", "text": str(obj), "url": obj.get_absolute_url()}

    def get_queryset(self):
        """Return queryset based on ModelAdmin.get_search_results()."""
        if _version >= 4:
            try:
                # django CMS 4.2+
                qs = list(
                    PageContent.admin_manager.filter(language=self.language, title__icontains=self.term)
                    .current_content()
                    .order_by("page__path")
                )
            except FieldError:
                # django CMS 4.0 - 4.1
                qs = list(
                    PageContent.admin_manager.filter(language=self.language, title__icontains=self.term)
                    .current_content()
                    .order_by("page__node__path")
                )
        else:
            # django CMS 3
            qs = list(PageContent.objects.filter(
                language=self.language, title__icontains=self.term
            ).order_by("page__node__path"))
            for page_content in qs:
                # Patch the missing get_absolute_url method
                page_content.get_absolute_url = lambda: page_content.page.get_absolute_url()
        return qs

    def process_request(self, request):
        """
        Validate request integrity, extract and return request parameters.
        """
        term = request.GET.get("term", "").strip("  ").lower()
        language = get_language_from_request(request)
        return term, language

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
    def has_module_permission(self, request):
        # Remove from admin
        return False

    def get_urls(self):
        return [
            path("urls",
                 self.admin_site.admin_view(self.url_view),
                 name=f"{self.opts.app_label}_{self.opts.model_name}_urls")
        ]

    def url_view(self, request):
        return UrlsJsonView.as_view(admin_site=self)(request)


admin.site.register(models.Link, LinkAdmin)
