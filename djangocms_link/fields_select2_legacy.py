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
        if self.site:
            return Page.objects.drafts().on_site(self.site)
        return Page.objects.drafts()

    def security_check(self, request, *args, **kwargs):
        user = request.user

        if user and not user.is_anonymous() and user.is_staff:
            return True
        return False
