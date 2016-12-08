from cms.models import Page
from django_select2.fields import AutoModelSelect2Field


class Select2LegacyPageSearchField(AutoModelSelect2Field):
    site = None
    search_fields = [
        'title_set__title__icontains',
        'title_set__menu_title__icontains',
        'title_set__slug__icontains'
    ]

    def get_queryset(self):
        return Page.objects.drafts().on_site(self.site) if self.site is not None else Page.objects.drafts()

    def security_check(self, request, *args, **kwargs):
        return request.user and not request.user.is_anonymous() and request.user.is_staff
